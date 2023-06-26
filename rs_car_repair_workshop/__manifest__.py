# -*- coding: utf-8 -*-
{
    'name': "Car Repair Workshop",

    'summary': """Fleet Repair Vehical Repair car maintenance Auto fleet service repair car
        """,

    'description': """
                Car repair services V14.0
    """,

    'author':"Redian Software pvt.ltd",
    'website': "http://www.rediansoftware.com",
    'category': 'Extra Tools',
    'version': '0.1',
    'support': 'krishna.y@rediansoftware.com',
    'version': '14.0.1.0.1',
    

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','purchase','stock','fleet','account'],

    # always loaded
    'license': 'LGPL-3',
    'currency': 'USD',
    'price': '25.0',
    'category': 'Feet',
    'data': [
         'security/ir.model.access.csv',
        'security/security.xml',
        'data/car.xml',
        'views/views.xml',
        'views/checklist_view.xml',
        'views/car_diagnosis_view.xml',
        'views/work_order.xml',
        'views/menu.xml',
        'views/hide_menu.xml',
        'views/inherited_views.xml',
        'wizard/update_technician.xml',
        'report/car_repair.xml'
    ],
    'images': [
        'static/description/banner.png'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets' : {
        'point_of_sale.assets': [
            'ks_pos_low_stock_alert/static/src/css/ks_low_stock.css',
            'ks_pos_low_stock_alert/static/src/js/ks_utils.js',
            'ks_pos_low_stock_alert/static/src/js/ks_low_stock.js',
            'ks_pos_low_stock_alert/static/src/js/ks_product_list.js',
            'ks_pos_low_stock_alert/static/src/js/ks_product_screen.js',
            'ks_pos_low_stock_alert/static/src/js/ks_product_widget.js',
        ],
        'web.assets_qweb': [
            'ks_pos_low_stock_alert/static/src/xml/**/*',
        ]
    }
}
