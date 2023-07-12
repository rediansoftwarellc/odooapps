from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Buyer(models.Model):
    _name = 'property.login'
    _description = "Create the Buyer's Details!............"

    already_register = fields.Boolean(string='Already Registered ?')
    new_user = fields.Boolean(string='New User ?')
    old_user_name = fields.Char(string='Username:-')
    old_password = fields.Char(string='Password:-')
    email = fields.Char(string='Email')
    mobile_no = fields.Char(string='Mobile No', size=10)
    new_user_name = fields.Char(string='Username:-')
    create_password = fields.Char(string='Create Password')
    confirm_password = fields.Char(string='Confirm Password')

    def action_to_login(self):  # IT TAKES TO USER TO SEE ALL PROPERTY AVAILABLE FOR SALE
        if self.already_register is True:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Property Available for Sale and Rental',
                'res_model': 'property.select',
                'domain': ['|', ('available_for', '=', 'rental'), ('available_for', '=', 'sale')],
                'view_mode': 'tree,form',
                'target': 'current',
            }

    def action_to_register(self):  # IT TAKES TO USER TO SEE ALL PROPERTY AVAILABLE FOR RENTAL
        if self.new_user is True:
            return {
                'res_model': 'property.login',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('01__property__management.login_form').id,
                'target': 'self',
            }
