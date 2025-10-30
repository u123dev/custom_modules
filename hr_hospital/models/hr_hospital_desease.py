from odoo import models, fields


class HrHospitalDesease(models.Model):
    _name = 'hr.hospital.desease'
    _description = 'Desease type'

    name = fields.Char(required=True)

    parent_id = fields.Many2one(
        comodel_name='hr.hospital.desease',
        string='Parent Disease',
        ondelete='restrict'
    )
    child_ids = fields.One2many(
        comodel_name='hr.hospital.desease',
        inverse_name='parent_id',
        string='Child Diseases'
    )

    code = fields.Char(string='ICD-10 Code', size=10)
    severity_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Danger Level', default='low')

    is_contagious = fields.Boolean(default=False)
    symptoms = fields.Text()
    spreading_region_ids = fields.Many2many(
        comodel_name='res.country',
        relation='hr_hospital_disease_country_rel',
        column1='disease_id',
        column2='country_id',
        string='Regions of Spread'
    )
