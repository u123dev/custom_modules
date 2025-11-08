import logging
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)


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
        # TO CLEAR: next parameter doesn't work correctly:
        #   warnings.warn(f'Property {self}.readonly should be
        #                   a boolean ({self.readonly}).')
        # readonly="visit_status in ['completed', 'missed']",
        help="Actual visit date/time; read-only when visit is finalized."
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

    diagnosis_count = fields.Integer(
        string='Number of Diagnoses',
        compute='_compute_diagnosis_count',
        store=True,
    )

    @api.depends('diagnosis_ids')
    def _compute_diagnosis_count(self):
        """Calculates the number of diagnoses linked to this visit."""
        for visit in self:
            visit.diagnosis_count = len(visit.diagnosis_ids)

    @api.onchange('patient_id')
    def _onchange_patient_id(self):  # pylint: disable=R1710,return-statements
        """Shows a warning if the patient has allergies."""
        if self.patient_id and self.patient_id.allergies:
            return {
                'warning': {
                    'title': _("Allergy Alert!"),
                    'message': _(
                        "The selected patient has registered allergies: "
                    ) + self.patient_id.allergies
                }
            }

    @api.onchange('doctor_id')
    # pylint: disable=R1710,return-statements
    def _onchange_doctor_id_substitute_mentor(self):
        """If the selected doctor is an intern,
        substitute them with their mentor."""
        if self.doctor_id and self.doctor_id.is_intern:
            _logger.warning(f"***** {self.doctor_id.name}")

            intern_doctor = self.doctor_id
            if intern_doctor.mentor_id:
                self.doctor_id = intern_doctor.mentor_id.id

                return {
                    'warning': {
                        'title': _("Intern Substitution"),
                        'message': _(
                            "The selected doctor is an intern and has "
                            "been substituted with their mentor: "
                        ) + intern_doctor.mentor_id.display_name,
                    }
                }

            return {
                'warning': {
                    'title': _("Intern as no mentor"),
                    'message': _(
                        "The selected intern doctor has no mentor."
                    )
                }
            }

    @api.constrains('doctor_id')
    def _check_doctor_license(self):
        """Check that doctor has a license number to be assigned to a visit."""
        for visit in self:
            if visit.doctor_id and not visit.doctor_id.license_number:
                raise ValidationError(_("Doctor must have a license number ")
                                      + visit.doctor_id.name)

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
                    + str(visit_date)
                )

    @api.constrains('planned_datetime', 'actual_datetime')
    def _check_actual_date_not_before_planned(self):
        """Checks that the actual visit datetime is not earlier
        than the planned datetime."""
        for visit in self:
            if (
                    visit.actual_datetime
                    and visit.planned_datetime
                    and visit.actual_datetime < visit.planned_datetime
            ):
                raise ValidationError(_(
                    "The actual visit datetime cannot be earlier "
                    "than the planned datetime."
                ))

    @api.constrains('doctor_id', 'planned_datetime', 'actual_datetime')
    def _check_critical_fields_for_finalized_visit(self):
        """Prohibits changing critical fields for finalized visit."""
        critical_fields = ['doctor_id', 'planned_datetime', 'actual_datetime']
        field_names = ", ".join(
            self._fields[f].string for f in critical_fields
        )
        if self.filtered(
                lambda rec: rec.visit_status in ['completed', 'missed']
        ):
            raise ValidationError(
                _("Modification for finalized visits is denied "
                  "for critical fields: ") + field_names
            )

    def unlink(self):
        """Prohibits deleting visits that already have associated diagnoses."""

        diagnosed_visits = self.filtered(lambda v: v.diagnosis_ids)
        if diagnosed_visits:
            raise UserError(_(
                "You cannot delete a visit that already has diagnoses. "
                "Please archive it instead."
            ))

        return super(HrHospitalVisit, self).unlink()
