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
    'name' : 'Website Stock',
    'version' : '14.0',
    'author' : 'Redian Software',
    'category' : 'Extra Tools',
    'description' : """

""",
    'summary': 'Notify when stock not available and you can identify stock in or out of stock',
    'website': "http://www.rediansoftware.com",
    'license': 'LGPL-3',
    'currency': 'USD',
    'price':   '29.0',
    'sequence': -200,
    'depends': ['base'],
    "data": [
        'views/product.xml',
    ],
    'test': [
    ],
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'auto_install': False,
}
