from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrHospitalDesease(models.Model):
    _name = 'hr.hospital.desease'
    _description = 'Desease type'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "name"
    _order = 'parent_path, name'

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
    parent_path = fields.Char(index=True)

    code = fields.Char(string='ICD-10 Code', size=10)
    severity_level = fields.Selection(selection=[
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

    @api.constrains('parent_id')
    def _check_desease_recursion(self):
        if not self._check_recursion():
            raise ValidationError(
                _("You cannot create recursive disease hierarchies!"))
