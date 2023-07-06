# -*- coding: utf-8 -*-
{
    'name': "Hide Action/Print Buttons",
    'summary': """ This module give user restriction to Show/Hide Action/Print buttons per user """,
    'author': 'Redian Software',
    'license': 'LGPL-3',
    'category': 'Tools',
    'sequence': -100,
    'version': '14.0',
    'currency': 'USD',
    'price': '27.0',
    'website': 'https://www.rediansoftware.com/',
    'depends': ['base', 'web', 'sale_management'],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'data': [
        'views/templates.xml',
        'security/security.xml',
    ],
    "images": ['static/description/icon.png'],

}
