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
    'name' : 'Delivery Date Scheduler.',
    'version' : '14.0',
    'author' : 'Redian Software',
    'category' : 'Extra Tools',
    'description' : """

""",
    "summary":"Using this module you can handle the delivery date created by customer on website",
    'website': "http://www.rediansoftware.com",
    'currency': 'USD',
    'price': '49.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'sequence': -107,
    'depends': ['product', 'sale_management', 'delivery', 'base', 'stock', 'sale_stock', 'website', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/del_date_sale_view.xml',
        'views/res_config_settings_view.xml',
        'views/delivery_setting_view.xml',
        'views/delivery_date_template.xml',
    ],
    'qweb' : [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
