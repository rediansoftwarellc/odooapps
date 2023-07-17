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
    'name' : 'Hide Action/Print Buttons.',
    'version' : '14.0',
    'author' : 'Redian Software',
    'category' : 'Extra Tools',
    'description' : """

""",
    "summary":"This module give user restriction to Show/Hide Action/Print buttons per user.!",
    'website': "http://www.rediansoftware.com",
    'currency': 'USD',
    'price':    '15.0',
    'license': 'LGPL-3',
    'sequence': -107,
    'depends': ['base', 'web', 'sale_management'],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'data': [
        'views/templates.xml',
        'security/security.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'auto_install': False,
}

