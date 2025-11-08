import logging
from odoo import models, fields, _
from odoo.odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class HrHospitalDiagnosis(models.Model):
    _name = 'hr.hospital.diagnosis'
    _description = 'Medical Diagnosis Record'
    _rec_name = 'disease_id'  # Display name based on the disease

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        required=True,
        ondelete='cascade'
    )
    disease_id = fields.Many2one(
        comodel_name='hr.hospital.desease',
        required=True
    )
    diagnosis_description = fields.Text()
    prescribed_treatment = fields.Html()
    severity_level = fields.Selection(selection=[
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('critical', 'Critical'),
    ], default='medium')
    is_approved = fields.Boolean(default=False)
    approving_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        readonly=True
    )
    approval_date = fields.Datetime(readonly=True)

    # Fielda for grouping
    doctor_related_id = fields.Many2one(
        comodelname='hr.hospital.doctor',
        related='visit_id.doctor_id',
        store=True,
        readonly=True
    )
    patient_country_related_id = fields.Many2one(
        comodelname='res.country',
        related='visit_id.patient_id.country_id',
        store=True,
        readonly=True
    )
    visit_date_related = fields.Datetime(
        related='visit_id.planned_datetime',
        store=True,
        readonly=True
    )

    def write(self, vals):
        """Check 'is_approved' diagnosis field and
        set the Approving Doctor (or Mentor if exists) and Approval Date."""

        if vals.get('is_approved'):
            visit_doctor = self.visit_id.doctor_id
            if not visit_doctor:
                raise UserError(_(
                    "Cannot approve the diagnosis: "
                    "The Doctor for the visit is not set."
                ))

            approving_doctor = visit_doctor.mentor_id or visit_doctor
            vals['approving_doctor_id'] = approving_doctor.id
            vals['approval_date'] = fields.Datetime.now()

            _logger.warning(
                f"***** Diagnosis {self.id}: "
                f"Fields added for Doctor: "
                f"{approving_doctor.id}, {approving_doctor.name}"
            )

        return super(HrHospitalDiagnosis, self).write(vals)
