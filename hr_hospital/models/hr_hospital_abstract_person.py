import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _


class HrHospitalAbstractPerson(models.AbstractModel):
    _name = 'hr.hospital.abstract.person'
    _description = 'Abstract Model for Person Data'

    _inherit = ['image.mixin']

    last_name = fields.Char(required=True)
    first_name = fields.Char(required=True)
    middle_name = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    birth_date = fields.Date()

    country_id = fields.Many2one(
        comodel_name='res.country',
        string="Country of Citizenship"
    )
    language_id = fields.Many2one('res.lang')

    name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
        recursive=True
    )
    age = fields.Integer(compute='_compute_age')

    @api.depends('last_name', 'first_name', 'middle_name')
    def _compute_full_name(self):
        """Computes the full name by joining the name parts."""
        for person in self:
            parts = [person.last_name, person.first_name, person.middle_name]
            person.name = ' '.join(filter(bool, parts))

    @api.depends('birth_date')
    def _compute_age(self):
        """Computes the age based on the date of birth."""
        today = fields.Date.today()
        for person in self:
            if person.birth_date:
                birth = person.birth_date
                person.age = today.year - birth.year - (
                    (today.month, today.day) < (birth.month, birth.day)
                )
            else:
                person.age = 0

    @api.constrains('phone')
    def _check_phone_format(self):
        """Validation that the phone field contains valid characters."""
        PHONE_REGEX = re.compile(r'^[0-9\s\-\+\(\)]+$')
        for record in self:
            if record.phone and not PHONE_REGEX.match(record.phone):
                raise ValidationError(_(
                    "Invalid phone format. "
                    "Only digits, spaces, and signs +, -, () are allowed."
                ))

    @api.constrains('email')
    def _check_email_format(self):
        """Simple validation for the email format."""
        EMAIL_REGEX = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        for record in self:
            if record.email and not EMAIL_REGEX.match(record.email):
                raise ValidationError(_("Invalid email address format."))
