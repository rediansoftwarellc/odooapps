
{
    'name': 'Hospital Management',
    'version': '1.0.0',
    'category': 'Hospital',
    'sequence': -111,
    'author': 'Redian Software',
    'currency': 'USD',
    'price': '27.0',
    'summary': 'Hospital Management System',
    'description': """ Hospital Management System""",
    'depends': ['mail','product'],
    'data': [
             'security/ir.model.access.csv',
             'Data/email_templates.xml',
             'views/menu.xml',
             'views/patient_view.xml',
             'views/female_patient_view.xml',
             'views/appointment_view.xml',
             'Data/data.xml',
             'views/patient_tag_view.xml',

             ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
