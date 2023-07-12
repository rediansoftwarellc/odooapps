from odoo import models, fields, api


class PaymentDetails(models.Model):
    _name = 'property.payment.details'
    _description = "This is your Payment Details."
    _rec_name = 'property_name1'

    property_name1 = fields.Many2one('property.select', string='Property Name:')
    monthly_rent1 = fields.Float(string='Rent/Month:', readonly=True)
    yearly_rent1 = fields.Float(string='Rent/Year:', readonly=True)
    total_area1 = fields.Integer(string='Area in SqFt:', readonly=True)
    price_perFT1 = fields.Float(string='Price/SqFt:', readonly=True)
    sale_price1 = fields.Float(string='Price for Sale:', readonly=True)

    @api.onchange('property_name1')
    def onchange_property_name1(self):  # It FETCHES the price and area details of the particular property
        if self.property_name1:
            self.monthly_rent1 = self.property_name1.monthly_rent
            self.yearly_rent1 = self.property_name1.yearly_rent
            self.total_area1 = self.property_name1.total_area
            self.price_perFT1 = self.property_name1.price_perFT
            self.sale_price1 = self.property_name1.sale_price
        else:
            self.monthly_rent1 = ''
            self.yearly_rent1 = ''
            self.total_area1 = ''
            self.price_perFT1 = ''
            self.sale_price1 = ''

    # @api.onchange('property_name1.agree')
    # def agree_onchange(self):
    #     if self.property_name1.agree is True:
    #         return self.agree1 is True

    def action_open_all_property_sale(self):  # IT TAKES TO USER TO SEE ALL PROPERTY AVAILABLE FOR SALE
        if self.property_name1.available_for == 'sale':
            return {
                'type': 'ir.actions.act_window',
                'name': 'Property Available for Sale',
                'res_model': 'property.select',
                'domain': [('available_for', '=', 'sale')],
                'view_mode': 'tree,form',
                'target': 'current',
            }

    def action_open_all_property_rental(self):  # IT TAKES TO USER TO SEE ALL PROPERTY AVAILABLE FOR RENTAL
        if self.property_name1.available_for == 'rental':
            return {
                'type': 'ir.actions.act_window',
                'name': 'Property Available for Sale',
                'res_model': 'property.select',
                'domain': [('available_for', '=', 'rental')],
                'view_mode': 'tree,form',
                'target': 'current',
            }

    def action_to_payment(self):  # IT TAKES TO USER TO SEE ALL PROPERTY AVAILABLE FOR RENTAL
        print('hhhhhhhhhhhhhhhhhhhhhhhhhhh')
