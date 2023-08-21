from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_name = fields.Many2one('res.users', string='Partner Name')
    colors = fields.Char(string='Colors')
    boolean = fields.Boolean(string='Boolean')
    amount = fields.Integer(string='Amount')
    notes = fields.Char(string='Notes')