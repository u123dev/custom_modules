from odoo import models, fields


class HrHospitalDesease(models.Model):
    _name = 'hr.hospital.desease'
    _description = 'Desease type'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()
