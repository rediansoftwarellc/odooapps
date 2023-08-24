# -*- coding: utf-8 -*-
##############################################################################
#
#    Redian Software Pvt Ltd
#    Copyright (C) 2016-Today(http://www.rediansoftware.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "All In One Import",
    'version': '14.0',
    'sequence': -109,
    'summary': ''' All Import Data of Odoo like Sales, Purchase, Invoice, Inventory,Bill of materia, Picking, Product, Customer ''',
    'description': "All In One import for sales, purchase, inventory and invoice",
    'author': 'Redian Software Pvt. Ltd.',
    'website': 'https://www.rediansoftware.com/',
    'depends': ['base', 'sale_management', 'purchase', 'mrp', 'account', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/mrp_import_view.xml',
        'views/account_move_view.xml',
        'views/stock_picking_view.xml',
        'wizard/import_sale_order_view.xml',
        'wizard/import_purchase_order_view.xml',
        'wizard/import_bom_view.xml',
        'wizard/import_account_move_view.xml',
        'wizard/import_stock_picking_view.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'license': 'LGPL-3',
    'currency': 'USD',
    'price': '49.0',
    'installable': True,
    'application': False,
    'auto_install': False
}
