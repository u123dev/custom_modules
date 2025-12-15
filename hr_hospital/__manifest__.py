{
    'name': 'HR Hospital Module',
    'summary': 'HR Hospital Module: Odoo Apps Publication',
    'author': 'u123dev',
    'website': 'https://github.com/u123dev',
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'version': '17.0.1.0.2',
    'price':  10.0,
    'currency': 'USD',

    'depends': [
        'base',
        'web',
        'mail'
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [

        'security/hr_hospital_security.xml',
        'security/ir.model.access.csv',
        'security/hr_hospital_rules.xml',

        'views/hr_hospital_menu.xml',

        'wizard/hr_hospital_mass_reassign_doctor_wizard_view.xml',
        'wizard/hr_hospital_desease_report_wizard_view.xml',
        'wizard/hr_hospital_reschedule_visit_wizard_view.xml',
        'wizard/hr_hospital_doctor_schedule_wizard_view.xml',
        'wizard/hr_hospital_patient_card_export_wizard_view.xml',

        'reports/hr_hospital_doctor_report.xml',

        'views/hr_hospital_desease_views.xml',
        'views/hr_hospital_visit_views.xml',
        'views/hr_hospital_doctor_views.xml',
        'views/hr_hospital_patient_views.xml',
        'views/hr_hospital_diagnosis_views.xml',
        'views/hr_hospital_doctor_schedule_view.xml',

    ],

    'demo': [
        'demo/hr_hospital_doctor_speciality_demo.xml',
        'demo/res_users_doctors_demo.xml',
        'demo/hr_hospital_doctor_demo.xml',
        'demo/res_users_patients_demo.xml',
        'demo/hr_hospital_patient_contact_demo.xml',
        'demo/hr_hospital_patient_doctor_history_demo.xml',
        'demo/hr_hospital_visit_demo.xml',
        'demo/hr_hospital_disease_demo.xml',
        'demo/hr_hospital_diagnosis_demo.xml',
        'demo/hr_hospital_doctor_schedule_demo.xml',
    ],

    'installable': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png'
    ],

}
