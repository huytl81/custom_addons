from odoo import fields, models, api
from odoo.exceptions import UserError


class DispatchDocumentCategory(models.Model):
    _name = "vtt.official.dispatch.category"
    _description = "Document Category"
    _check_company_auto = True

    name = fields.Char('Name', required=True,
                       copy=False, default='New')
    code = fields.Char('Code', required=True,
                       copy=False, default='', size=4)
    description = fields.Char('Description', copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Code must be unique.')
    ] #Unique Codes

    def name_get(self):
        """
        Name get with record's name and code.
        """
        res = []
        for category in self:
            name = category.name if not category.code else '%s - %s' % (
                category.code, category.name)
            res.append((category.id, name))
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """
        Name search with code.
        """
        args = list(args or [])
        if not (name == '' and operator == 'ilike'):
            args += ['|', (self._rec_name, operator, name),
                     ('code', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def unlink(self):
        """
        Restrict unlink if record still referenced.
        """
        for rec in self:
            ref_request = self.env['vtt.official.dispatch.request.line'].search(
                [('category_id', '=', self.id)])
            ref_doc = self.env['vtt.official.dispatch.document'].search(
                [('category_id', '=', self.id)])
            if len(ref_request) or len(ref_doc):
                raise UserError(
                    "This category are still referenced by another record, therefore cannot be deleted.")
        super(DispatchDocumentCategory, self).unlink()
