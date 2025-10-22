{
    'name': 'HR Hospitaly Module',
    'summary': '',
    'author': 'u123dev',
    'website': 'https://github.com/u123dev',
    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '17.0.0.0.3',

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

        'data/hr_hospital_desease_data.xml',

    ],

    'demo': [
        'demo/hr_hospital_demo.xml',
    ],

    'installable': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png'
    ],

}
