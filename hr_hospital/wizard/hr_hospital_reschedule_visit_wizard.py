import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time, timedelta

_logger = logging.getLogger(__name__)


class HrHospitalRescheduleVisitWizard(models.TransientModel):
    _name = 'hr.hospital.reschedule.visit.wizard'
    _description = 'Reschedule Patient Visit'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        required=True,
        readonly=True,
    )
    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        related='visit_id.patient_id',
        readonly=True
    )
    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
        domain="[('license_number', '!=', False)]"
    )
    new_date = fields.Date(
        required=True,
        default=fields.Date.today
    )
    new_time = fields.Float(
        required=True,
        help='Time of the new visit in 24-hour format (f.e., 9.5 for 09:30).'
    )
    reschedule_reason = fields.Text(
        string='Reschedule Reason',
        required=True
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-fill the visit_id based on the active context."""
        res = super(HrHospitalRescheduleVisitWizard,
                    self).default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id:
            visit = self.env['hr.hospital.visit'].browse(active_id)
            res['visit_id'] = visit.id
            res['new_doctor_id'] = visit.doctor_id.id
            if visit.planned_datetime:
                res['new_date'] = visit.planned_datetime.date()
                res['new_time'] = visit.planned_datetime.hour + (
                            visit.planned_datetime.minute / 60.0)

        return res

    @api.constrains('new_date')
    def _check_new_date(self):
        """Ensure the new date is not in the past."""
        for rec in self:
            if rec.new_date < fields.Date.today():
                raise ValidationError(_("The new date cannot be in the past."))

    def action_reschedule_visit(self):
        """Cancel the current visit and create a new visit record."""
        self.ensure_one()
        current_visit = self.visit_id

        if current_visit.visit_status != 'planned':
            raise UserError(_(
                "Only 'Planned' visits can be rescheduled. "
                "Current status is: ") + current_visit.visit_status)

        # new planned_datetime
        hours = int(self.new_time)
        minutes = int((self.new_time - hours) * 60)
        new_datetime = datetime.combine(self.new_date, time(hours, minutes))

        # Check unique visit manually before creating
        domain = [
            ('patient_id', '=', current_visit.patient_id.id),
            ('doctor_id', '=', self.new_doctor_id.id),
            ('id', '!=', current_visit.id),  # Exclude original visit
            # Check for other visits on the same day
            ('planned_datetime', '>=', new_datetime.date()),
            ('planned_datetime', '<', new_datetime.date() + timedelta(days=1)),
        ]

        if self.env['hr.hospital.visit'].search(domain):
            raise ValidationError(
                _("Patient is already booked on this new date/time.")
            )

        # Update current visit status (Cancel old slot)
        current_visit.write({
            'visit_status': 'cancelled',
            'recommendations': (current_visit.recommendations or '') +
                               f'<p><strong>Visit Cancelled (Rescheduled):'
                               f'</strong> {self.reschedule_reason}</p>'
        })

        # Create new visit record
        new_visit = self.env['hr.hospital.visit'].create({
            'patient_id': current_visit.patient_id.id,
            'doctor_id': self.new_doctor_id.id,
            'planned_datetime': new_datetime,
            'visit_type': current_visit.visit_type,
            'visit_cost': current_visit.visit_cost,
            'recommendations': f'<p><strong>Rescheduled From Visit:</strong>'
                               f' {current_visit.id}. '
                               f'Reason: {self.reschedule_reason}</p>',
            'currency_id': current_visit.currency_id.id,
        })

        # Return action to view the new visit
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'res_id': new_visit.id,
            'view_mode': 'form',
            'target': 'current',
            'context': self._context,
        }
