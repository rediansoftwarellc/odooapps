{
    'name': 'Product Warranty',
    'version': '14.0',
    'sequence': -108,
    'summary': 'This app related to renew product warranty',
    'description': 'This app related to renew product warranty',
    'author': 'Redian Software',
    'currency': 'USD',
    'price': '27.0',
    'website': 'https://www.rediansoftware.com/',
    'ref': 'https://apps.odoo.com/apps/modules/16.0/bi_warranty_registration/',
    'depends': ['product', 'sales_warranty', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/warranty_view.xml',
        'reports/report_view.xml',
        'views/warranty_tags.xml',
        'views/warranty_teams.xml',
        'views/warranty_renew.xml',
        'wizards/warranty_renewal_view.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'

}
