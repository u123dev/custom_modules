from odoo import models, fields


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Patient Visit'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True
    )
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True
    )
    desease_ids = fields.Many2many(
        comodel_name='hr.hospital.desease',
        relation='hr_hospital_patient_desease_rel',
        column1='patient_id',
        column2='desease_id',
    )
    visit_datetime = fields.Datetime(
        required=True,
        default=fields.Datetime.now
    )
    anamnesis = fields.Text()
    diagnosis = fields.Text()
    description = fields.Text()
