from odoo import fields, models, _, api


class WarrantyTeam(models.Model):
    _name = 'warranty.team'
    _description = 'warranty team'

    name = fields.Char(string="Warranty Team")
    team_leader_id = fields.Many2one('res.users', string='Team Leader', default=lambda self: self.env.user)
