from odoo import models, fields, api, _

class Account(models.Model):
    _inherit = 'account.move'

    partner_name = fields.Many2one('res.users', string='Partner Name')
    colors = fields.Many2many("account.partner.color", string='Colors')
    color = fields.Char(string='Color')
    boolean = fields.Boolean(string='Boolean')
    amount = fields.Integer(string='Amount')
    notes = fields.Char(string='Notes')


class PartnerColor(models.Model):
    _name = "account.partner.color"
    _description = "Partner Color"

    name = fields.Char(string='Color Name')