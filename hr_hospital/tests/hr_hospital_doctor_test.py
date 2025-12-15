from datetime import date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class TestHrHospitalDoctorMentor(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Doctor = self.env['hr.hospital.doctor']
        self.User = self.env['res.users']
        self.Visit = self.env['hr.hospital.visit']
        self.Patient = self.env['hr.hospital.patient']
        self.Speciality = self.env['hr.hospital.doctor.speciality']

        self.user_mentor = self.User.create({
            'name': 'Mentor User', 'login': 'mentor_login',
            'email': 'mentor@hospital.com',
        })
        self.user_intern = self.User.create({
            'name': 'Intern User', 'login': 'intern_login',
            'email': 'intern@hospital.com',
        })
        self.user_new = self.User.create({
            'name': 'New User', 'login': 'new_login',
            'email': 'new@hospital.com',
        })
        self.user_test = self.User.create({
            'name': 'Test User Compute', 'login': 'test_compute',
            'email': 'compute@hospital.com',
        })

        self.spec_cardio = self.Speciality.create({'name': 'Cardiology',
                                                   'code': 'C001'})

        self.mentor_doctor = self.Doctor.create({
            'first_name': 'John',
            'last_name': 'Smith',
            'license_number': 'LIC001',
            'user_id': self.user_mentor.id,
            'is_intern': False,
            'license_issue_date': date.today() - relativedelta(years=5),
            'speciality_id': self.spec_cardio.id,
        })

        self.intern_doctor = self.Doctor.create({
            'first_name': 'Jane',
            'last_name': 'Doe',
            'license_number': 'LIC002',
            'user_id': self.user_intern.id,
            'is_intern': True,
            'mentor_id': self.mentor_doctor.id,
        })

        self.doc_to_be_mentored = self.Doctor.create({
            'first_name': 'Doc',
            'last_name': 'Test',
            'license_number': 'LIC004',
            'user_id': self.user_new.id,
            'is_intern': True,
        })

        self.test_patient = self.Patient.create({
            'first_name': 'Test',
            'last_name': 'Patient',
            'phone': '1234567890',
        })

    def test_doctor_mentor_constraints(self):
        """
        Test that intern can't be mentor.
        Test that self-mentoring is forbidden.
        """

        with self.assertRaisesRegex(
                ValidationError,
                "An intern cannot be a mentor."):
            self.doc_to_be_mentored.mentor_id = self.intern_doctor.id

        with self.assertRaisesRegex(
                ValidationError,
                "A doctor cannot be a mentor to themself."):
            self.mentor_doctor.mentor_id = self.mentor_doctor.id

        self.doc_to_be_mentored.mentor_id = self.mentor_doctor.id
        self.assertEqual(
            self.doc_to_be_mentored.mentor_id,
            self.mentor_doctor,
            "Valid mentor must be assigned successfully."
        )

    def test_doctor_check_archiving_with_active_visits(self):
        """
        Test that a doctor with active/planned visits cannot be archived.
        Test that a doctor with completed visits can be archived.
        """

        test_visit = self.Visit.create({
            'patient_id': self.test_patient.id,
            'doctor_id': self.mentor_doctor.id,
            'planned_datetime': date.today() + relativedelta(days=7),
            'visit_status': 'planned',  # Active status
        })

        with self.assertRaisesRegex(
                ValidationError,
                "Doctor who has active visits can't be archived"
        ):
            self.mentor_doctor.active = False

        test_visit.visit_status = 'completed'  # Inactive status

        self.mentor_doctor.active = False
        self.assertFalse(
            self.mentor_doctor.active,
            "Archiving of doctor with non-active visits should pass."
        )

    def test_doctor_compute_display_name(self):
        """
        Test the computation of the doctor's display_name with speciality.
        Test the computation of the doctor's display_name without speciality.
        """

        expected_name_with_spec = (f"{self.mentor_doctor.name} "
                                   f"({self.spec_cardio.name})")
        self.assertEqual(
            self.mentor_doctor.display_name,
            expected_name_with_spec,
            "Display name should include name and speciality."
        )

        expected_name_no_spec = self.intern_doctor.name
        self.assertEqual(
            self.intern_doctor.display_name,
            expected_name_no_spec,
            "Display name for doctor without speciality "
            "should just be only name."
        )
