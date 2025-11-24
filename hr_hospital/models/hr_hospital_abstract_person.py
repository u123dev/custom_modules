import re
from odoo import models, fields, api, _
from odoo.odoo.exceptions import ValidationError


class HrHospitalAbstractPerson(models.AbstractModel):
    _name = 'hr.hospital.abstract.person'
    _description = 'Abstract Model for Person Data'

    _inherit = ['image.mixin', 'hr.hospital.date.mixin']

    last_name = fields.Char(required=True, translate=True)
    first_name = fields.Char(required=True, translate=True)
    middle_name = fields.Char(translate=True)
    phone = fields.Char()
    email = fields.Char()
    gender = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    birth_date = fields.Date()

    country_id = fields.Many2one(
        comodel_name='res.country',
        string="Country of Citizenship"
    )
    language_id = fields.Many2one(comodel_name='res.lang')

    name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
        index=True,
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
        """Compute age in full years based on the birth date."""
        for person in self:
            person.age = self._calculate_years(person.birth_date)

    @api.constrains('phone')
    def _check_phone_format(self):
        """Validation that the phone field contains valid characters."""
        PHONE_REGEX = re.compile(r'^[0-9\s\-\+\(\)]+$')
        if self.filtered(
                lambda rec: rec.phone and not PHONE_REGEX.match(rec.phone)
        ):
            raise ValidationError(_(
                "Invalid phone format. "
                "Only digits, spaces, and signs +, -, () are allowed."
            ))

    @api.constrains('email')
    def _check_email_format(self):
        """Unicode-aware validation for email format (RFC-compatible)."""
        EMAIL_REGEX = re.compile(
            r"(^[-!#$%&'*+/0-9=?A-Z^_`a-z{|}~\u00A0-\uFFFF]+"
            r"(\.[-!#$%&'*+/0-9=?A-Z^_`a-z{|}~\u00A0-\uFFFF]+)*"
            r"|^\"([!#-\[\]-~ \t\u00A0-\uFFFF]|(\\[\t -~\u00A0-\uFFFF]))+\""
            r")@([A-Za-z0-9\u00A0-\uFFFF](?:[A-Za-z0-9\u00A0-\uFFFF-]{0,61}"
            r"[A-Za-z0-9\u00A0-\uFFFF])?\.)+"
            r"[A-Za-z\u00A1-\uFFFF]{2,}$",
            re.UNICODE
        )

        for record in self:
            if record.email and not EMAIL_REGEX.match(record.email):
                raise ValidationError(_("Invalid email address format."))
