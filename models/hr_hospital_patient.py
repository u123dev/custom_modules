from odoo import models, fields


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'

    name = fields.Char(required=True)
    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female')
        ]
    )
    birth_date = fields.Date()
    age = fields.Integer(compute='_compute_age')
    phone = fields.Char()
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Family Doctor'
    )

    def _compute_age(self):
        today = fields.Date.today()
        for patient in self:
            if patient.birth_date:
                birth = patient.birth_date
                patient.age = today.year - birth.year - (
                    (today.month, today.day) < (birth.month, birth.day)
                )
            else:
                patient.age = 0
