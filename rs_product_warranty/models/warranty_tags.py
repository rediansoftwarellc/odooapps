from odoo import fields, models, _, api


class WarrantyTags(models.Model):
    _name = 'warranty.tags'
    _description = 'warranty tags'

    name = fields.Char(string="Tag Name")
    description = fields.Char(string="Description")