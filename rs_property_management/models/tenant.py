from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Tenant(models.Model):
    _name = 'property.tenant'
    _description = "Create the Tenant's Details!............"

    tenant_name = fields.Char(string='Tenant Name')
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
    agree = fields.Boolean(string='Agree To Rent')

    # @api.constrains('contact_no')  # It is for the Contact NO. Validation(Used OnChange)
    # def check_contact_no(self):
    #     for rec in self:
    #         if len(rec.contact_no) < 10:
    #             raise ValidationError(_('Contact No. should be of  10 Characters'))

    def action_open_to_rent(self):  # it takes to the form of PRICE details of the House
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
            raise ValidationError(_("Please fill the details and Check on 'Agree For Rent'"))
