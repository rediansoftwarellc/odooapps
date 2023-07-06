from odoo import fields, models, _, api


class Warrantyhistory(models.Model):
    _name = 'warranty.history'
    _description = 'warranty history'

    current_date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    start_date = fields.Date(string="Warranty Start Date")
    end_date = fields.Date(string='Warranty End Date')
    warranty_type = fields.Char(string='Warranty Type')
    warranty_id = fields.Many2one('product.warranty', string='Product Warranty')
    r_amount = fields.Float(string='Renewal amount')

class Category(models.Model):
    _name = "category"
    _description = "Category"

    name = fields.Char(string='Category')

