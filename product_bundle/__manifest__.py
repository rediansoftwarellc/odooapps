{
    'name': 'Product Bundle',
    'version': '14.0',
    'author': 'Redian Software pvt. Ltd.',
    'author': 'Redian Software',
    'currency': 'USD',
    'price': '27.0',
    'category': 'Sales',
    'sequence': -107,
    'depends': ['sale_management', 'product', 'sale_stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_bundle_view.xml',
    ],
    'installable': True,
    'application': True,
}

