from odoo import models, fields


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
    severity_level = fields.Selection([
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
