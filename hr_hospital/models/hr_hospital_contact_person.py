from odoo import models


class HrHospitalContactPerson(models.Model):
    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'

    _inherit = ['hr.hospital.abstract.person']
