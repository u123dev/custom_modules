import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class HrHospitalMassReassignDoctorWizard(models.TransientModel):
    _name = 'hr.hospital.mass.reassign.doctor.wizard'
    _description = 'Mass Doctor Reassignment Wizard'

    old_doctor_id = fields.Many2one(comodel_name='hr.hospital.doctor')
    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
    )
    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        required=True,
    )
    change_date = fields.Date(
        required=True,
        default=fields.Date.today
    )
    change_reason = fields.Text(required=True)

    @api.model
    def default_get(self, fields):
        """Pre-fill patient_ids and old_doctor_id based on selected records."""
        result = super(HrHospitalMassReassignDoctorWizard,
                       self).default_get(fields)

        # Get the IDs of records selected by the user in the list view
        active_ids = self.env.context.get('active_ids')

        if not active_ids:
            return result

        # Load selected patient records
        patients = self.env['hr.hospital.patient'].browse(active_ids)

        if not patients:
            return result

        # Set patient_ids (M2M field) using the 'set' command (6, 0, [IDs])
        if 'patient_ids' in fields:
            result['patient_ids'] = [(6, 0, patients.ids)]

        # Determine the common Old Doctor among selected patients
        # We take the doctor of the FIRST patient as the default,
        # and then filter the patient list based on this doctor.

        first_patient = patients[0]
        if first_patient.personal_doctor_id:
            old_doctor = first_patient.personal_doctor_id
            result['old_doctor_id'] = old_doctor.id

            # Filter patients for currently assigned to this doctor
            filtered_patients = patients.filtered(
                lambda p: p.personal_doctor_id == old_doctor
            )

            # Update patient_ids with the filtered list
            if 'patient_ids' in fields and filtered_patients:
                result['patient_ids'] = [(6, 0, filtered_patients.ids)]

        return result

    @api.onchange('old_doctor_id')
    def _onchange_old_doctor_id(self):
        """Filters the list of patients by the selected old doctor."""
        if self.old_doctor_id:
            # domain for the patient_ids field: only patients of the old doctor
            domain = [('personal_doctor_id', '=', self.old_doctor_id.id)]
            # patient_ids field with all patients of this doctor
            self.patient_ids = self.env['hr.hospital.patient'].search(domain)
        else:
            # If the old doctor is not selected, clear patient list and domain
            self.patient_ids = False
            domain = []

        # Return the dynamic domain for the patient_ids field
        return {'domain': {'patient_ids': domain}}

    def action_reassign_doctor(self):
        """Performs mass doctor reassignment and creates history records."""
        self.ensure_one()

        if self.new_doctor_id == self.old_doctor_id:
            raise UserError(_(
                "New Doctor must be different from the Old Doctor."))

        if not self.patient_ids:
            raise UserError(_("Please select patients to reassign."))

        _logger.info(
            f"Mass reassignment: {len(self.patient_ids)} patients from "
            f"doctor {self.old_doctor_id.name if self.old_doctor_id else '--'}"
            f" (ID: {self.old_doctor_id.id if self.old_doctor_id else 0}) to "
            f"doctor {self.new_doctor_id.name} (ID: {self.new_doctor_id.id})"
        )

        # Prepare context to pass wizard data (date and reason)
        context_data = {
            'history_change_date': self.change_date,
            'history_change_reason': self.change_reason,
            'history_is_mass_reassignment': True,
        }

        # with_context() will use the wizard's date and reason
        # instead of system defaults.
        self.patient_ids.with_context(context_data).write({
            'personal_doctor_id': self.new_doctor_id.id
        })

        return {'type': 'ir.actions.act_window_close'}
