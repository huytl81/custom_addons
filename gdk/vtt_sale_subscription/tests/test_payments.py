# -*- coding: utf-8 -*-
import datetime
import unittest.mock

from odoo import fields
from odoo.exceptions import AccessError

from odoo.addons.payment.tests.common import PaymentCommon
from odoo.addons.sale_subscription.tests.common_sale_subscription import TestSubscriptionCommon


class TestSubscriptionPayments(PaymentCommon, TestSubscriptionCommon):

    # Mocking for 'test_auto_payment_with_token'
    # Necessary to have a valid and done transaction when the cron on subscription passes through
    def _mock_subscription_do_payment(self, payment_token, invoice, two_steps_sec=True):
        reference = "CONTRACT-%s-%s" % (self.id, datetime.datetime.now().strftime('%y%m%d_%H%M%S'))
        values = {
            'amount': invoice.amount_total,
            'acquirer_id': self.dummy_acquirer.id,
            'operation': 'offline',
            'currency_id': invoice.currency_id.id,
            'reference': reference,
            'token_id': payment_token.id,
            'partner_id': invoice.partner_id.id,
            'partner_country_id': invoice.partner_id.country_id.id,
            'invoice_ids': [(6, 0, [invoice.id])],
            'state': 'done',
        }
        return self.create_transaction(flow='token', **values)

    # Mocking for 'test_auto_payment_with_token'
    # Otherwise the whole sending mail process will be triggered
    # And we are not here to test that flow, and it is a heavy one
    def _mock_subscription_send_success_mail(self, tx, invoice):
        self.mock_send_success_count += 1
        return 666

    # Mocking for 'test_auto_payment_with_token'
    # Avoid account_id is False when creating the invoice
    def _mock_prepare_invoice_data(self):
        invoice = self.original_prepare_invoice_data()
        invoice['partner_bank_id'] = False
        return invoice

    # Mocking for 'test_auto_payment_with_token'
    # Avoid account_id is False when creating the invoice
    def _mock_prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        line_values = self.original_prepare_invoice_line(
            line, fiscal_position, date_start, date_stop
        )
        return line_values

    def test_auto_payment_with_token(self):
        from unittest.mock import patch

        self.company = self.env.company
        self.company.country_id = self.env.ref('base.us')

        self.account_type_receivable = self.env['account.account.type'].create({
            'name': 'receivable',
            'type': 'receivable',
            'internal_group': 'asset',
        })

        self.account_receivable = self.env['account.account'].create(
            {'name': 'Ian Anderson',
             'code': 'IA',
             'user_type_id': self.account_type_receivable.id,
             'company_id': self.company.id,
             'reconcile': True})

        self.account_type_sale = self.env['account.account.type'].create({
            'name': 'income',
            'type': 'other',
            'internal_group': 'income',
        })
        self.account_sale = self.env['account.account'].create(
            {'name': 'Product Sales ',
             'code': 'S200000',
             'user_type_id': self.account_type_sale.id,
             'company_id': self.company.id,
             'reconcile': False})

        self.sale_journal = self.env['account.journal'].create(
            {'name': 'reflets.info',
             'code': 'ref',
             'type': 'sale',
             'company_id': self.company.id,
             'default_account_id': self.account_sale.id})

        self.partner = self.env['res.partner'].create(
            {'name': 'Stevie Nicks',
             'email': 'sti@fleetwood.mac',
             'property_account_receivable_id': self.account_receivable.id,
             'property_account_payable_id': self.account_receivable.id,
             'company_id': self.company.id})

        self.original_prepare_invoice_data = self.subscription._prepare_invoice_data
        self.original_prepare_invoice_line = self.subscription._prepare_invoice_line

        patchers = [
            patch(
                'odoo.addons.vtt_sale_subscription.models.vtt_sale_subscription.SaleSubscription'
                '._prepare_invoice_line',
                wraps=self._mock_prepare_invoice_line
            ),
            patch(
                'odoo.addons.vtt_sale_subscription.models.vtt_sale_subscription.SaleSubscription'
                '._prepare_invoice_data',
                wraps=self._mock_prepare_invoice_data
            ),
            patch(
                'odoo.addons.vtt_sale_subscription.models.vtt_sale_subscription.SaleSubscription'
                '._do_payment',
                wraps=self._mock_subscription_do_payment
            ),
            patch(
                'odoo.addons.vtt_sale_subscription.models.vtt_sale_subscription.SaleSubscription'
                '.send_success_mail',
                wraps=self._mock_subscription_send_success_mail
            ),
        ]

        for patcher in patchers:
            patcher.start()

        self.subscription_tmpl.payment_mode = 'success_payment'

        self.subscription.write({
            'partner_id': self.partner.id,
            'recurring_next_date': fields.Date.to_string(datetime.date.today()),
            'template_id': self.subscription_tmpl.id,
            'company_id': self.company.id,
            'payment_token_id': self.create_token().id,
            'recurring_invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'name': 'TestRecurringLine',
                'price_unit': 50,
                'uom_id': self.product.uom_id.id
            })],
            'stage_id': self.ref('vtt_sale_subscription.sale_subscription_stage_in_progress'),
        })
        self.subscription.recurring_invoice_line_ids.onchange_product_id()
        self.mock_send_success_count = 0
        self.subscription.with_context(auto_commit=False)._recurring_create_invoice(automatic=True)
        self.assertEqual(
            self.mock_send_success_count, 1, 'a mail to the invoice recipient should have been sent'
        )
        self.assertEqual(
            self.subscription.stage_category,
            'progress',
            'subscription with online payment and a payment method set should stay opened when '
            'transaction succeeds'
        )

        invoice_id = self.subscription.action_subscription_invoice()['res_id']
        invoice = self.env['account.move'].browse(invoice_id)
        recurring_total_with_taxes = self.subscription.recurring_total + (
                    self.subscription.recurring_total * (self.tax_10.amount / 100.0))
        self.assertEqual(
            invoice.amount_total,
            recurring_total_with_taxes,
            'website_subscription: the total of the recurring invoice created should be the '
            'subscription recurring total + the products taxes'
        )
        self.assertTrue(
            all(line.tax_ids.ids == self.tax_10.ids for line in invoice.invoice_line_ids),
            'website_subscription: All lines of the recurring invoice created should have the '
            'percent tax set on the subscription products'
        )
        self.assertTrue(
            all(
                tax_line.tax_line_id == self.tax_10
                for tax_line in invoice.line_ids.filtered('tax_line_id')
            ),
            'The invoice tax lines should be set and should all use the tax set on the subscription'
            ' products'
        )

        for patcher in patchers:
            patcher.stop()

    def test_prevents_assigning_not_owned_payment_tokens_to_subscriptions(self):
        malicious_user_subscription = self.env['sale.subscription'].create({
            'name': 'Free Subscription',
            'partner_id': self.malicious_user.partner_id.id,
            'template_id': self.subscription_tmpl.id,
        })
        self.partner = self.env['res.partner'].create(
            {'name': 'Stevie Nicks',
             'email': 'sti@fleetwood.mac',
             'property_account_receivable_id': self.account_receivable.id,
             'property_account_payable_id': self.account_receivable.id,
             'company_id': self.env.company.id})
        stolen_payment_method = self.env['payment.token'].create(
            {'name': 'Jimmy McNulty',
             'partner_id': self.partner.id,
             'acquirer_id': self.dummy_acquirer.id,
             'acquirer_ref': 'Omar Little'})

        with self.assertRaises(AccessError):
            malicious_user_subscription.with_user(self.malicious_user).write({
                'payment_token_id': stolen_payment_method.id,
                # payment token not related to al capone
            })

    def test_do_payment_calls_send_payment_request_only_once(self):
        self.invoice = self.env['account.move'].create(
            self.subscription._prepare_invoice()
        )
        with unittest.mock.patch(
            'odoo.addons.payment.models.payment_transaction.PaymentTransaction'
            '._send_payment_request'
        ) as patched:
            self.subscription._do_payment(self.create_token(), self.invoice)
            patched.assert_called_once()
