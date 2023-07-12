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
    'name' : 'Product Barcode Scanning',
    'version' : '14.0',
    'author' : 'Redian Software',
    'category' : 'Extra Tools',
    'description' : """

""",
    "summary":"You can create product directly throgh the Barcode No.!",
    'website': "http://www.rediansoftware.com",
    'currency': 'USD',
    'price': '27.0',
    'license': 'LGPL-3',
    'sequence': -145,
    'depends': ['sale_management', 'purchase', 'stock'],
    'data':['views/views.xml'],
    'qweb' : [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
