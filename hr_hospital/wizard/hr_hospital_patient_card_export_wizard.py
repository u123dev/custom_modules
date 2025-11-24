import logging
from datetime import timedelta
import json
import csv
from io import StringIO
import base64
from odoo import models, fields, api, _
from odoo.odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class HrHospitalPatientCardExportWizard(models.TransientModel):
    _name = 'hr.hospital.patient.card.export.wizard'
    _description = 'Wizard to Export Patient Medical Card'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True
    )
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')

    include_diagnoses = fields.Boolean(default=True)
    include_recommendations = fields.Boolean(default=True)

    report_language_id = fields.Many2one(
        comodel_name='res.lang',
        required=True,
        default=lambda self: self._get_default_language_id(),
    )
    export_format = fields.Selection([
        ('json', 'JSON'),
        ('csv', 'CSV'),
    ], required=True, default='json')

    export_file = fields.Binary(readonly=True)
    file_name = fields.Char(readonly=True)

    @api.model
    def _get_default_language_id(self):
        """Sets the default report language based on the current user."""
        user_lang_code = self.env.user.lang
        return self.env['res.lang'].search([('code', '=', user_lang_code)],
                                           limit=1).id

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """Sets the default report language based on the patient's language."""
        if self.patient_id and self.patient_id.language_id:
            self.report_language_id = self.patient_id.language_id.id
        else:
            self.report_language_id = self._get_default_language_id()

    def _get_diagnosis_data(self):
        """Fetches and filters the patient's diagnosis data and transforms it
        into a flat list for export."""
        if not self.include_diagnoses and not self.include_recommendations:
            return []

        # Search domain: by patient
        domain = [('visit_id.patient_id', '=', self.patient_id.id)]

        # Date filtering
        if self.date_start:
            domain.append(('visit_date_related', '>=', self.date_start))
        if self.date_end:
            # +1 day as last day
            date_end_inclusive = fields.Datetime.to_datetime(
                self.date_end) + timedelta(days=1)
            domain.append(('visit_date_related', '<', date_end_inclusive))

        # Fetch diagnoses
        diagnoses = self.env['hr.hospital.diagnosis'].search(domain)
        export_data = []

        # Get selection values
        severity_selection = dict(
            self.env['hr.hospital.diagnosis']._fields[
                'severity_level'].selection)

        for diag in diagnoses:
            record = {
                'Visit_Date': fields.Datetime.to_string(
                    diag.visit_date_related),
                'Doctor_Name': diag.doctor_related_id.name,
            }
            has_content = False

            # Include primary diagnosis information
            if self.include_diagnoses:
                record.update({
                    'Diagnosis_Name': diag.disease_id.name,
                    'Diagnosis_Description': diag.diagnosis_description or '',
                    'Severity': severity_selection.get(diag.severity_level,
                                                       ''),
                    'Approved': diag.is_approved,
                })
                has_content = True

            # Include recommendations (diagnosis-specific and visit-general)
            if self.include_recommendations:
                # Diagnosis-specific treatment (prescribed_treatment)
                record['Diagnosis_Treatment'] = diag.prescribed_treatment or ''

                # Visit-general recommendations
                record['Visit_General_Recommendations'] = (
                    diag.visit_id.recommendations or ''
                )

                if (record['Diagnosis_Treatment'] or
                        record['Visit_General_Recommendations']):
                    has_content = True

            # Only add the record if it contains data we intended to include
            if has_content:
                export_data.append(record)

        return export_data

    def action_export_card(self):
        """Initiate the export in the selected format."""
        self.ensure_one()

        data_to_export = self._get_diagnosis_data()

        if not data_to_export:
            raise UserError(
                _("No data to export based on the specified criteria."))

        filename = f"patient_card_{self.patient_id.name.replace(' ', '_')}"

        if self.export_format == 'json':
            content = json.dumps(data_to_export, ensure_ascii=False, indent=4)
            filename += '.json'
        elif self.export_format == 'csv':
            content = self._generate_csv(data_to_export)
            filename += '.csv'
        else:
            raise UserError(_("Unsupported export format."))

        # Base64
        content_base64 = base64.b64encode(content.encode('utf-8'))
        self.write({
            'export_file': content_base64,
            'file_name': filename,
        })

        # binary field
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/hr.hospital.patient.card.export.wizard/'
                   f'{self.id}/export_file/{self.file_name}',
            'target': 'self',
        }

    def _generate_csv(self, data):
        """Generate CSV string."""
        if not data:
            return ""

        fieldnames = list(data[0].keys())

        output = StringIO()

        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(data)

        # add BOM (Byte Order Mark) for UTF-8  (for Excel compatibility)
        csv_string = u'\ufeff' + output.getvalue()
        return csv_string
