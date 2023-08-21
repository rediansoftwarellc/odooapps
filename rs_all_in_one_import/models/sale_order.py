from odoo import fields, api, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_partner_id = fields.Many2one('res.users', string='Partner')
    x_partner_ids = fields.Many2many('partner.color', string='Colors')
    x_color = fields.Many2one('partner.color', string='Colors')
    x_bool = fields.Boolean(string='Boolean', default=False)
    x_amount = fields.Integer(string='Amount')
    x_notes = fields.Char(string='Notes')

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Disc.%')

class PartnerColor(models.Model):
    _name = "partner.color"
    _description = "Partner Color"

    name = fields.Char(string='Color Name')