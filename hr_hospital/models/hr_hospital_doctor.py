from odoo import models, fields


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'

    name = fields.Char(required=True)
    speciality = fields.Char()
    qualification = fields.Char()
    phone = fields.Char()
    is_fulltime = fields.Boolean(default=True)
