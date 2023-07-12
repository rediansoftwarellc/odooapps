from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Buyer(models.Model):
    _name = 'property.buyer'
    _description = "Create the Buyer's Details!............"
    _rec_name = 'buyer_name'

    buyer_name = fields.Char(string='Buyer Name')
    age = fields.Integer(string='Age')
    contact_no = fields.Char(string='Contact No.', size=10)
    email = fields.Char(string='Email')
    UID = fields.Char(string='Aadhaar No.')
    PAN = fields.Char(string='PAN Card No.')

    Indian = fields.Boolean(string='Indian')
    address = fields.Text(string='Address')
    state = fields.Many2one('res.country.state', string='State')
    city = fields.Char(string='City')
    pincode = fields.Integer(string='Pincode')
    country = fields.Many2one('res.country', string='Country')
    agree = fields.Boolean(string='Agree To Buy')

    def action_open_to_buy(self):  # it takes to the form to Price  details of the House
        if self.agree is True:
            return {
                'res_model': 'property.payment.details',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('01__property__management.payment_details_form').id,
                'target': 'current',
            }
        else:
            raise ValidationError(_("Please fill the details and Click on 'Agree To Buy'"))
