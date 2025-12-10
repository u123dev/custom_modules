import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrHospitalDiseaseReportWizard(models.TransientModel):
    _name = 'hr.hospital.disease.report.wizard'
    _description = 'Disease Report Wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors',
        help='If empty, all doctors will include.'
    )
    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.desease',
        string='Diseases',
        help='If empty, all diseases will include.'
    )
    country_ids = fields.Many2many(
        comodel_name='res.country',
        string='Countries',
        help='Filters by the country of patient.'
    )

    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.today() - timedelta(days=90)
    )
    date_to = fields.Date(required=True, default=fields.Date.today)

    report_type = fields.Selection(selection=[
        ('detailed', 'Detailed'),
        ('summary', 'Summary'),
    ], default='detailed', required=True)

    group_by = fields.Selection(selection=[
        ('doctor', 'Doctor'),
        ('disease', 'Disease'),
        ('month', 'Month'),
        ('country', 'Country'),
    ], default='disease', required=True)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate that date_from is not later than date_to."""
        for record in self:
            if record.date_from > record.date_to:
                raise UserError(
                    _("Date From cannot be later than Date To."))

    def action_generate_report(self):
        """Generate report based on selected criteria."""
        self.ensure_one()

        domain = [
            ('visit_id.planned_datetime', '>=',
             fields.Datetime.to_datetime(self.date_from)),
            ('visit_id.planned_datetime', '<',
             fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)),
        ]

        # Filter by doctors
        if self.doctor_ids:
            domain.append(('visit_id.doctor_id', 'in', self.doctor_ids.ids))
        # Filter by diseases
        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))
        # Filter by patient countries
        if self.country_ids:
            domain.append(
                ('visit_id.patient_id.country_id', 'in', self.country_ids.ids))

        # --- Map user choice to the Related Fields ---
        group_field_map = {
            'doctor': 'doctor_related_id',
            'disease': 'disease_id',
            'month': 'visit_date_related:month',
            'country': 'patient_country_related_id',
        }
        group_by_field_name = group_field_map.get(self.group_by)

        # Fetch diagnosis (search by domain)
        diagnoses = self.env['hr.hospital.diagnosis'].search(domain)
        if not diagnoses:
            raise UserError(
                _("No diagnoses found for the selected criteria."))

        _logger.info(
            f"Disease report generated: {len(diagnoses)} diagnoses found. "
            f"Filters: doctors={self.doctor_ids.mapped('name') or 'All'}, "
            f"diseases={self.disease_ids.mapped('name') or 'All'}, "
            f"countries={self.country_ids.mapped('name') or 'All'}, "
            f"period={self.date_from} to {self.date_to}, "
            f"report_type={self.report_type} "
        )

        context_data = {}

        if self.report_type == 'summary':
            # Summary uses Pivot View for aggregation
            view_mode = 'pivot,tree,form'
            report_name = _('Summary Disease Report')
            context_data['pivot_measures'] = ['__count']
        else:
            # Detailed uses Tree View
            view_mode = 'tree,form'
            report_name = _('Detailed Disease Report')

        # Set Group By command for both modes using related fields
        if group_by_field_name:
            context_data['group_by'] = group_by_field_name

        return {
            'name': report_name,
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.diagnosis',
            'view_mode': view_mode,
            'domain': [('id', 'in', diagnoses.ids)],
            'context': context_data,
        }
