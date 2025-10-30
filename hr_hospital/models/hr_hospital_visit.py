from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo import _


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True
    )
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True
    )

    visit_status = fields.Selection([
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed'),
    ], default='planned')

    visit_type = fields.Selection([
        ('primary', 'Primary'),
        ('repeat', 'Repeat'),
        ('preventive', 'Preventive'),
        ('urgent', 'Urgent'),
    ], default='primary')

    planned_datetime = fields.Datetime(required=True)

    actual_datetime = fields.Datetime(
        string='Actual Datetime',
        readonly=True,  # Readonly unless status is 'completed'
        help='Actual date and time of the visit.'
    )
    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.diagnosis',
        inverse_name='visit_id',
        string='Diagnoses'
    )
    recommendations = fields.Html()
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    visit_cost = fields.Monetary(currency_field='currency_id')

    @api.constrains('patient_id', 'doctor_id', 'planned_datetime')
    def _check_unique_visit_per_day(self):
        """Prohibits booking the same patient to the same doctor
        more than once a day."""
        for visit in self:
            if not visit.planned_datetime:
                continue

            visit_date = visit.planned_datetime.date()

            domain = [
                ('id', '!=', visit.id),
                ('patient_id', '=', visit.patient_id.id),
                ('doctor_id', '=', visit.doctor_id.id),
                # Check for other visits on the same day
                ('planned_datetime', '>=', visit_date),
                ('planned_datetime', '<', visit_date + timedelta(days=1)),
            ]

            existing_visits = self.env['hr.hospital.visit'].search(domain)

            if existing_visits:
                raise ValidationError(
                    _("Patient is already booked to doctor on this date: ")
                    + visit_date
                )

    @api.constrains('planned_datetime', 'actual_datetime')
    def _check_actual_date_not_before_planned(self):
        """Checks that the actual visit datetime is not earlier
        than the planned datetime."""
        for visit in self:
            if visit.actual_datetime and visit.planned_datetime:
                if visit.actual_datetime < visit.planned_datetime:
                    raise ValidationError(_(
                        "The actual visit datetime cannot be earlier "
                        "than the planned datetime."
                    ))

    def write(self, vals):
        """Prohibits changing critical fields for finalized visit."""

        critical_fields = ['doctor_id', 'planned_datetime', 'actual_datetime']
        fields_changed = set(critical_fields) & set(vals.keys())

        if fields_changed:
            completed_visits = self.filtered(
                lambda v: v.visit_status in ['completed', 'missed']
            )

            if completed_visits:
                field_metadata = self.fields_get()
                field_descriptions = [
                    field_metadata[f]['string']
                    for f in fields_changed
                    if f in field_metadata and field_metadata[f].get('string')
                ]
                fields_str = ', '.join(field_descriptions)

                raise ValidationError(
                    _("Modification is prohibited for finalized visits "
                      "for critical fields: ") + f"[{fields_str}]"
                )

        return super(HrHospitalVisit, self).write(vals)

    def unlink(self):
        """Prohibits deleting visits that already have associated diagnoses."""

        diagnosed_visits = self.filtered(lambda v: v.diagnosis_ids)

        if diagnosed_visits:
            raise UserError(_(
                "You cannot delete a visit that already has diagnoses. "
                "Please archive it instead."
            ))

        return super(HrHospitalVisit, self).unlink()
