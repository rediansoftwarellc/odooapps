from odoo import fields, models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    partner_name = fields.Many2one('res.users', string='Partner Name')
    color = fields.Char(string='Color')
    boolean = fields.Boolean(string='Boolean')
    amount = fields.Integer(string='Amount')
    notes = fields.Char(string='Notes')