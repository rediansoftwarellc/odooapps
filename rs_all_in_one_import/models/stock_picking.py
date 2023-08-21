from odoo import fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_name = fields.Char(string='Partner Name')
    color = fields.Char(string='Color')
    boolean = fields.Boolean(string='Boolean')
    amount = fields.Integer(string='Amount')
    notes = fields.Char(string='Notes')