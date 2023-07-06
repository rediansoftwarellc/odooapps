# __manifest__.py

{
    'name': 'Subscription',
    'version': '1.0',
    'summary': 'Manage Subscriptions with Start Date and Duration',
    'description': 'This module allows you to manage subscriptions with start date and duration in Odoo 14.',
    'author': 'Redian Software',
    'currency': 'USD',
    'price': '27.0',
    'category': 'Uncategorized',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/subs.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
