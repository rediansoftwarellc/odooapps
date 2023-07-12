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
    'name' : 'Hospital Management',
    'version' : '14.0',
    'author' : 'Redian Software',
    'category' : 'Extra Tools',
    'description' : """

""",
    "summary":"Using this module you can get the appointment from doctor with date and Time !",
    'website': "http://www.rediansoftware.com",
    'currency': 'USD',
    'price':    '29.0',
    'license': 'LGPL-3',
    'sequence': -107,
    'depends': ['mail','product'],
    'data': [
        'security/ir.model.access.csv',
             'Data/email_templates.xml',
             'views/menu.xml',
             'views/patient_view.xml',
             'views/female_patient_view.xml',
             'views/appointment_view.xml',
             'Data/data.xml',
             'views/patient_tag_view.xml',
    ],
    'qweb' : [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

