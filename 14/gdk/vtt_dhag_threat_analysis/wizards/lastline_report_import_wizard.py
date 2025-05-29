# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64, json
from bs4 import BeautifulSoup
import ast


def get_eval_list(lst):
    return [eval(item) for item in lst]


def get_recursive_obj(soup_node):
    if not soup_node.findChildren(recursive=False):
        return soup_node.text
    else:
        lst = [s.name for s in soup_node.findChildren(recursive=False)]
        # lst_no_dup = list(set(lst))
        if 'element' in lst:
            return [get_recursive_obj(s) for s in soup_node.findChildren(recursive=False)]
        else:
            return {s.name:get_recursive_obj(s) for s in soup_node.findChildren(recursive=False)}


class LastlineReportImportWizard(models.TransientModel):
    _name = 'lastline.report.import.wizard'
    _description = 'Lastline XML Report Import Wizard'

    file_datas = fields.Binary('XML file')

    def _get_default_investigate(self):
        return self.env['investigate.investigate'].browse(self.env.context.get('active_id')) or False

    investigate_id = fields.Many2one('investigate.investigate', 'Investigate', default=_get_default_investigate)

    def _get_default_mapper(self):
        default_lastline_mapper = self.env.ref('vtt_dhag_threat_analysis.vtt_threat_field_mapper_lastline', raise_if_not_found=False)
        if default_lastline_mapper:
            return default_lastline_mapper
        else:
            return self.env['threat.subject.field.mapper'].search([('code', '=', 'LL')], limit=1)

    subject_field_mapper = fields.Many2one('threat.subject.field.mapper', 'Fields Mapper', default=_get_default_mapper)

    def import_from_xml_report(self):
        if self.file_datas:
            soup = BeautifulSoup(base64.decodebytes(self.file_datas), features="lxml")
            doc_result = soup.find('result')
            if doc_result:
                result_success_check = doc_result.find('success', recursive=False)
                if bool(result_success_check.text):
                    res_data = doc_result.find('data', recursive=False)
                    res_data_score = res_data.find('score', recursive=False)
                    res_data_analysis_subject = res_data.find('analysis_subject', recursive=False)
                    res_data_malicious_activity = res_data.find('malicious_activity', recursive=False)
                    res_data_child_tasks = res_data.find('child_tasks', recursive=False)

                    malware_vals = {}

                    malicious = []
                    malicious_summary = get_recursive_obj(res_data_malicious_activity)
                    for m in malicious_summary:
                        sp = m.split(': ')
                        malicious.append({
                            "title": sp[0],
                            "content": sp[1],
                        })

                    malware_vals.update({
                        "md5": res_data_analysis_subject.find('md5').text,
                        "sha1": res_data_analysis_subject.find('sha1').text,
                        "sha256": res_data_analysis_subject.find('sha256').text,
                        "mime_type": res_data_analysis_subject.find('mime_type').text,
                        "score_float": res_data_score.text,
                        "dt_submission": res_data.find('submission', recursive=False).text,
                        "malicious_activity": json.dumps(malicious, indent=2),
                        "child_tasks": json.dumps(get_recursive_obj(res_data_child_tasks), indent=2)
                    })

                    # In-effect after State manager
                    # if self.investigate_id:
                    #     malware_vals.update({
                    #         "investigate_id": self.investigate_id.id
                    #     })

                    if malware_vals:
                        new_malware_id = self.env['threat.malware'].create(malware_vals)

                        # For State manager
                        if self.investigate_id:
                            self.investigate_id.write({
                                'investigate_malware_ids': [(0, 0, {
                                    'malware_id': new_malware_id.id,
                                    'state': 'doubt',
                                })]
                            })

                        # Insert Analysis subjects
                        subject_val_list = []
                        analysis_subjects = res_data.find('analysis_subjects')
                        if analysis_subjects:
                            subjects = analysis_subjects.findChildren(recursive=False)
                            if self.subject_field_mapper:
                                rules = self.subject_field_mapper.mapped('line_ids')
                            else:
                                rules = False
                            for s in subjects:
                                subject_vals = {
                                    "malware_id": new_malware_id.id
                                }
                                # Overview
                                overview = s.find('overview', recursive=False)
                                if overview:
                                    subject_vals.update({
                                        "md5": overview.find('md5').text if overview.find('md5') else "",
                                        "sha1": overview.find('sha1').text if overview.find('sha1') else "",
                                        "sha256": overview.find('sha256').text if overview.find('sha256') else "",
                                        "command_line": overview.find('filename').text if overview.find('filename') else "",
                                    })
                                # Info by Mapper
                                if rules:
                                    for r in rules:
                                        if s.find(r.src_tag):
                                            subject_vals.update({
                                                r.res_field: json.dumps(get_recursive_obj(s.find(r.src_tag)), indent=2)
                                            })

                                if subject_vals:
                                    subject_val_list.append(subject_vals)

                            if subject_val_list:
                                self.env['threat.malware.subject'].create(subject_val_list)

        return {'type': 'ir.actions.act_window_close'}