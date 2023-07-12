from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re


class Property(models.Model):
    _name = 'property.select'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = 'Create the property details!............'
    _rec_name = 'property_name'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))  # field of sequence
    active = fields.Boolean(string='Active', default=True)  # for archived in action
    property_name = fields.Char(string='Property Name:', required='True', tracking=True)
    owner_name = fields.Char(string='Owner Name:')
    contact_no = fields.Char(string='Contact No.', size=10)
    email = fields.Char(string='Email:')

    available = fields.Selection([('yes', 'Yes'), ('no', 'No'), ], string='Available..?', required='True')
    status = fields.Selection([('sold', 'Sold'), ('booked', 'Booked')], string='Status:')
    available_for = fields.Selection([('rental', 'Rental'), ('sale', 'Sale')],
                                     string='Available For:')
    property_type = fields.Selection([('bungalow', 'Bungalow'), ('flat', 'Flat'),
                                      ('villa', 'Villa')], string='Property type:')
    flat = fields.Selection([('1bhk', '1BHK'), ('2bhk', '2BHK'),
                             ('3bhk', '3BHK'), ('4bhk', '4BHK')], string='Flat:')

    monthly_rent = fields.Float(string='Rent/Month:')
    yearly_rent = fields.Float(string='Rent/Year:', compute='compute_yearly_rent')
    total_area = fields.Integer(string='Area in SqFt:')
    price_perFT = fields.Float(string='Price/SqFt:')
    sale_price = fields.Float(string='Price for Sale:', compute='compute_sale_price')

    Indian = fields.Boolean(string='Indian:')
    address = fields.Text(string='Address:')
    state = fields.Many2one('res.country.state')
    city = fields.Char()
    pincode = fields.Integer()
    country = fields.Many2one('res.country')
    image = fields.Image(string='property Image:')


    # this is the code for the sequence
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('property.select.sequence')
        result = super(Property, self).create(vals)
        return result

    @api.onchange('monthly_rent')  # (Used Compute field and Onchange )
    def compute_yearly_rent(self):  # It calculates the yearly rent based on monthly rent
        for rec in self:
            rec.yearly_rent = rec.monthly_rent * 12

    @api.onchange('price_perFT', 'total_area')
    def compute_sale_price(self):  # It calculates the Price for sale(price) based on price/SqFt and total area
        for a in self:
            self.sale_price = self.price_perFT * self.total_area

    def action_open_rental(self):  # it takes to the form to fill details of the Tenant
        if self.available_for == 'rental':
            return {
                'res_model': 'property.tenant',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('01__property__management.tenant_form').id,
                'target': 'self',
            }
        else:  # it throws an error if property is NOT available or available for SALE
            raise ValidationError(_("This Property is NOT Available For Buying"))

    def action_open_buyer(self):  # it takes to the form to fill details of the buyer
        if self.available_for == 'sale':
            return {
                'res_model': 'property.buyer',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('01__property__management.buyer_form').id,
                'target': 'self',
            }
        else:  # it throws an error if property is NOT available or available for RENTAL
            raise ValidationError(_("This Property is NOT Available For Rental"))

    @api.onchange('available')  # It makes the fields clear if no availability of the property
    def onchange_available(self):
        if self.available == 'no':
            self.available_for = ''
            self.property_type = ''
            self.flat = ''
        if self.available == 'yes':  # It makes the status fields clear  if there is availability of the property
            self.status = ''

    # constrains for the Mobile no. should be unique
    _sql_constraints = [('contact_no_unique', 'UNIQUE(contact_no)', 'This mobile no is already Exists!..')]

    @api.constrains('contact_no')  # Mobile no. Validation(no character only digits and 10 digits)
    def _check_contact_no(self):
        for rec in self:
            if rec.contact_no and not str(rec.contact_no).isdigit():
                raise ValidationError(_("Mobile No. should be Numeric"))
            if rec.contact_no and len(rec.contact_no) != 10:
                raise ValidationError(_("'Mobile No. should be of 10 Characters'..."))
        return True

    @api.onchange('email')  # Code for the email Validation
    def validate_mail(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match is None:
                raise ValidationError(_('Please Enter Valid Email ID....!'))
