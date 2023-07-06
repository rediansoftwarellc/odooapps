{
    'name': 'Delivery deadline',
    'version': '14.0',
    'author': 'Redian Software',
    'currency': 'USD',
    'price': '27.0',
    'category': 'Sales',
    'sequence': -107,
    'depends': ['sale_management', 'product', 'sale_stock', 'purchase', 'mrp'],
    'data': [
        'views/delivery_deadline_views.xml',
    ],
# https://apps.odoo.com/apps/modules/16.0/sales_mrp_deadline_delivery_date/
    'installable': True,
    'application': True,
}

