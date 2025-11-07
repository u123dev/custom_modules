{
    'name': 'HR Hospitaly Module',
    'summary': '',
    'author': 'u123dev',
    'website': 'https://github.com/u123dev',
    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '17.0.0.0.5',

    'depends': [
        'base',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [

        'security/ir.model.access.csv',

        'views/hr_hospital_menu.xml',

        'views/hr_hospital_desease_views.xml',
        'views/hr_hospital_doctor_views.xml',
        'views/hr_hospital_patient_views.xml',
        'views/hr_hospital_visit_views.xml',
        'views/hr_hospital_diagnosis_views.xml',
        'views/hr_hospital_doctor_schedule_view.xml',

        'wizard/hr_hospital_mass_reassign_doctor_wizard_view.xml',
        'wizard/hr_hospital_desease_report_wizard_view.xml',
        'wizard/hr_hospital_reschedule_visit_wizard_view.xml',
        'wizard/hr_hospital_doctor_schedule_wizard_view.xml',
        'wizard/hr_hospital_patient_card_export_wizard_view.xml',

        'data/hr_hospital_desease_data.xml',

    ],

    'demo': [
        'demo/hr_hospital_demo.xml',

        # 'demo/hr_hospital_doctor_speciality_demo.xml',
        # 'demo/res_users_doctors_demo.xml',
        # 'demo/hr_hospital_doctor_demo.xml',
        # 'demo/ hr_hospital_patient_contact_demo.xml',
        # 'demo/hr_hospital_patient_doctor_history_demo.xml',
        # 'demo/hr_hospital_visit_demo.xml',
        # 'demo/hr_hospital_disease_demo.xml',
        # 'demo/hr_hospital_diagnosis_demo.xml',
        # 'demo/hr_hospital_doctor_schedule_demo.xml',
    ],

    'installable': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png'
    ],

}
