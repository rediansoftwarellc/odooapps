# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#    Redian Software pvt.ltd                                                  #            #
#    Copyright (C) 2016-Today Redian Software(https://www.rediansoftware.com/)#
#                                                                             # 
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # 
#    GNU Affero General Public License for more details.                      #
#                                                                             #
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################

{   'name': 'Whatsapp Massage',
    'version': '14.0.0.1',
    'category': 'Generic Modules',
    'sequence':-111,
    'author':  "Redian Software pvt.ltd",
    'website': "https://www.rediansoftware.com/",
    'license': 'LGPL-3',
    'currency': 'USD',
    'price': '15.0',
   
    'name': "Whatsapp Massage",

    'summary': """Redian Software Whatsapp Massage to give you  send massages to our partner and send message to customer with details of saleorder and invoice via whatsapp""",
    'sequence':-111,
    'description': """
        Redian Software Whatsapp Massage to give you  send massages to our partner and send message to customer with
       details of saleorder and invoice via whatsap
    """,
#--------------------------------------------------------------------------------------    
    'depends': ['base','contacts','sale','account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/whatsapp_wizard.xml',
        'views/views.xml',
    ],
    'images': [
        'static/description/whatsapp_message.png'
    ],
    'demo': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
