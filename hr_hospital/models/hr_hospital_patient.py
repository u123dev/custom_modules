from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'

    _inherit = ['hr.hospital.abstract.person']

    personal_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        ondelete='set null'
    )
    passport_data = fields.Char(size=10)
    contact_person_id = fields.Many2one(
        comodel_name='hr.hospital.contact.person'
    )
    insurance_company_id = fields.Many2one(
        comodel_name='res.partner',
        domain=[('is_company', '=', True)]
    )
    insurance_policy_number = fields.Char()
    blood_group = fields.Selection([
        ('O1+', 'O (I) Rh+'),
        ('O1-', 'O (I) Rh-'),
        ('A2+', 'A (II) Rh+'),
        ('A2-', 'A (II) Rh-'),
        ('B3+', 'B (III) Rh+'),
        ('B3-', 'B (III) Rh-'),
        ('AB4+', 'AB (IV) Rh+'),
        ('AB4-', 'AB (IV) Rh-'),
    ])
    allergies = fields.Text()
    doctor_history_ids = fields.One2many(
        comodel_name='hr.hospital.patient.doctor.history',
        inverse_name='patient_id',
        string='Personal Doctor History'
    )

    @api.constrains('birth_date')
    def _check_patient_age(self):
        """Checks that the patient's age is greater than 0
        (birth date must be in the past)."""
        today = fields.Date.today()
        for patient in self:
            if patient.birth_date and patient.birth_date >= today:
                raise ValidationError(
                    _("The patient's date of birth must be in the past."))

    def write(self, vals):
        """Create a history record when personal_doctor_id changes."""

        if 'personal_doctor_id' in vals:
            for patient in self:
                old_doctor_id = patient.personal_doctor_id.id
                new_doctor_id = vals.get('personal_doctor_id')

                if patient.id and old_doctor_id != new_doctor_id:

                    current_active_history = (
                        self.env['hr.hospital.patient.doctor.history'].search(
                            [
                                ('patient_id', '=', patient.id),
                                ('is_active', '=', True)
                            ], limit=1))

                    if current_active_history:
                        current_active_history.write({
                            'is_active': False,
                            'change_date': fields.Date.today()
                        })

                    if new_doctor_id:
                        self.env['hr.hospital.patient.doctor.history'].create({
                            'patient_id': patient.id,
                            'doctor_id': new_doctor_id,
                            'assignment_date': fields.Date.today(),
                            'is_active': True,
                        })

        return super(HrHospitalPatient, self).write(vals)
