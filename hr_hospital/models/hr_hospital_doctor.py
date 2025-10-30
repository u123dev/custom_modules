from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'

    _inherit = ['hr.hospital.abstract.person']

    # speciality = fields.Char()
    # qualification = fields.Char()
    # is_fulltime = fields.Boolean(default=True)

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='System User',
        required=True,
        ondelete='restrict',
        help='The user associated with this doctor for system login.'
    )
    license_number = fields.Char(required=True, copy=False, size=32)
    license_issue_date = fields.Date()
    work_experience = fields.Integer(
        string='Work Experience (Years)',
        compute='_compute_work_experience',
        store=True,
        help='Work Experience (from the license issue date).'
    )
    speciality_id = fields.Many2one(
        comodel_name='hr.hospital.doctor.speciality'
    )
    is_intern = fields.Boolean()
    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        domain=[('is_intern', '=', False)],
        help='The assigned mentor doctor (available only for interns).'
    )
    rating = fields.Float(digits=(3, 2), default=0.00)
    country_of_study_id = fields.Many2one(comodel_name='res.country')
    schedule_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.schedule',
        inverse_name='doctor_id',
        string='Work Schedule'
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('license_number_unique',
         'UNIQUE (license_number)',
         'The License Number must be unique.'),

        ('rating_check',
         'CHECK (rating >= 0.00 AND rating <= 5.00)',
         'Doctor rating must be between 0.00 and 5.00.'),
    ]

    @api.depends('license_issue_date')
    def _compute_work_experience(self):
        """Calculates work experience in years from the license issue date."""
        today = fields.Date.today()
        for doctor in self:
            if doctor.license_issue_date:
                issue_date = doctor.license_issue_date
                experience = (today.year - issue_date.year -
                              (
                                  (today.month, today.day) <
                                  (issue_date.month, issue_date.day)
                              )
                              )
                doctor.work_experience = experience if experience >= 0 else 0
            else:
                doctor.work_experience = 0

    @api.constrains('license_number')
    def _check_license_number_unique(self):
        """Ensures the license number is unique."""
        for doctor in self:
            if doctor.license_number:
                existing = self.env['hr.hospital.doctor'].search([
                    ('license_number', '=', doctor.license_number),
                    ('id', '!=', doctor.id)
                ])
                if existing:
                    raise ValidationError(
                        _("The License Number must be unique.")
                    )

    @api.constrains('mentor_id')
    def _check_mentor_is_not_intern(self):
        """Prohibits selecting an intern as a mentor."""
        for doctor in self:
            if doctor.mentor_id and doctor.mentor_id.is_intern:
                raise ValidationError(_("An intern cannot be a mentor."))

    @api.constrains('mentor_id')
    def _check_self_mentoring(self):
        """Prohibits a doctor from being their own mentor."""
        for doctor in self:
            if doctor.mentor_id and doctor.mentor_id.id == doctor.id:
                raise ValidationError(
                    _("A doctor cannot be a mentor to themself.")
                )

    @api.constrains('active')
    def _check_archiving_with_active_visits(self):
        """Prohibits archiving doctors who have active
        (non-completed/non-cancelled) visits."""
        for doctor in self:
            if not doctor.active:
                active_visits = self.env['hr.hospital.visit'].search([
                    ('doctor_id', '=', doctor.id),
                    ('visit_status', 'in', ['planned', 'urgent'])
                    # Visits that are not completed/cancelled/missed
                ], limit=1)

                if active_visits:
                    raise ValidationError(_(
                        "You cannot archive a doctor who still has active"
                        " or planned visits. "
                        "Please cancel or complete all pending visits first."
                    ))
