import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


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

    @api.onchange('country_id')
    def _onchange_country_id(self):  # pylint: disable=R1710,return-statements
        """Change language according to the selected country."""

        # Mapping countries with language code
        language_code_map = {
            'gb': 'en',  # Great Britain (UK)
            'us': 'en',  # United States (US)
            'ca': 'en',  # Canada (CA)
            'ua': 'uk',  # Ukraine (UA)
            'ru': 'ru',  # Russia (RU)
        }
        if self.country_id:
            # search for a language with a code matching the country's code
            country_code = self.country_id.code.lower()
            base_lang_code = language_code_map.get(country_code, country_code)
            lang_record = False
            if base_lang_code:
                # Search for specific regional code (f.ex.: uk_UA)
                lang_record = self.env['res.lang'].search([
                    ('code', 'ilike', f'{base_lang_code}_%')
                ], limit=1)

                if not lang_record:
                    # If not, Search for exact base language code (f.ex.: 'uk')
                    lang_record = self.env['res.lang'].search([
                        ('code', '=', base_lang_code)
                    ], limit=1)

            if lang_record:
                self.language_id = lang_record.id
                _logger.warning(f"***** Language set for country "
                                f"{country_code}: {lang_record.code}")
            else:
                _logger.warning(f"***** Language not found for country "
                                f"{country_code}.")
                return {
                    'warning': {
                        'title': _("Language not found"),
                        'message': _(
                            "Language not found for country."
                        )
                    }
                }

    @api.constrains('birth_date')
    def _check_patient_age(self):
        """Checks that the patient's age is greater than 0
        (birth date must be in the past)."""
        today = fields.Date.today()
        if self.filtered(lambda p: p.birth_date and p.birth_date >= today):
            raise ValidationError(
                _("The patient's date of birth must be in the past.")
            )

    def write(self, vals):
        """Create a history record when personal_doctor_id changes."""

        if 'personal_doctor_id' not in vals:
            return super(HrHospitalPatient, self).write(vals)

        # Get date and reason from context (passed by wizard) or use defaults
        assignment_date = self.env.context.get('history_change_date',
                                               fields.Date.today())
        change_reason = self.env.context.get('history_change_reason', False)

        data = []

        for patient in self.filtered(
                lambda x: x.personal_doctor_id != vals['personal_doctor_id']):
            history_record = ({
                'patient_id': patient.id,
                'doctor_id': vals['personal_doctor_id'],
                'assignment_date': assignment_date,
                'active': True,
            })

            # Add change_reason only if it exists in the history model
            if change_reason:
                history_record['change_reason'] = change_reason

            data.append(history_record)

        result = super(HrHospitalPatient, self).write(vals)
        if data:
            self.env['hr.hospital.patient.doctor.history'].sudo().create(data)
        return result
