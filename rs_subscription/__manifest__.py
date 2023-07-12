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
    'name' : ' Sale Warranty',
    'version' : '14.0',
    'author' : 'Redian Software',
    'category' : 'Extra Tools',
    'description' : """

""",
    'summary': 'This app related to Create warranty, update product warranty, warranty status by saleorder',
    'website': "http://www.rediansoftware.com",
    'license': 'LGPL-3',
    'currency': 'USD',
    'price':    '35.0',
    'sequence': -200,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/subs.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
