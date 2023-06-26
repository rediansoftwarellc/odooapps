from odoo import models,fields,api,_

class CheckLists(models.Model):
    _name = 'car.checklist'
    _description = 'Here we will store all car related checklist.'
    _rec_name='cheklists_name'
    cheklists_name=fields.Char('Checklist Name')
    created_by=fields.Many2one('res.users','Created By' ,default=lambda self: self.env.user,readonly=1)

