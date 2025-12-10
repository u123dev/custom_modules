from odoo import api, fields, models


class PatientDoctorHistory(models.Model):
    _name = 'hr.hospital.patient.doctor.history'
    _description = 'Patient Doctor Assignment History'

    name = fields.Char(
        string='Assignment Record',
        compute='_compute_name',
        store=True,
        help='Display name combining patient, doctor, and date.'
    )
    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True,
        ondelete='cascade'
    )
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True
    )
    assignment_date = fields.Date(
        required=True,
        default=fields.Date.today
    )
    change_date = fields.Date()
    change_reason = fields.Text()
    active = fields.Boolean(
        default=True,
        help='Indicates the current doctor assignment.'
    )

    @api.depends('patient_id', 'doctor_id', 'assignment_date')
    def _compute_name(self):
        """Generates the display name for the history record."""
        for record in self:
            patient_name = record.patient_id.name or 'N/A Patient'
            doctor_name = record.doctor_id.name or 'N/A Doctor'
            date_str = record.assignment_date.strftime('%Y-%m-%d') \
                if record.assignment_date else 'N/A Date'

            record.name = (f"Assignment: {patient_name} to {doctor_name} "
                           f"({date_str})")

    @api.model_create_multi
    def create(self, vals_list):
        """Deactivate previous active records for each patient
        before creating new ones."""

        for vals in vals_list:
            patient_id = vals.get('patient_id')

            if patient_id:
                # Find all active history records for patient
                previous_records = self.search([
                    ('patient_id', '=', patient_id),
                    ('change_date', '=', False),
                    ('active', '=', True)
                ])

                # Deactivate them
                if previous_records:
                    previous_records.write({'active': False})

        return super().create(vals_list)

    def write(self, vals):
        """Update change_date to current date when record is modified."""
        vals['change_date'] = fields.Date.today()
        return super().write(vals)
