from odoo import api, fields, models, _


class HelpDesk(models.Model):
    _name = "help.desk"
    _description = "Help Desk"

    customer_id = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    note = fields.Text(string='Description')
    reason = fields.Selection([('damage', 'Damage'), ('faulty', 'Faulty'), ('lost', 'Lost')], string='Reason')
    start_date = fields.Date(string='Issue Start Date', default=fields.Date.context_today, readonly=True)
    end_date = fields.Date(string='Issue End Date', readonly=True)
    email = fields.Char(string='Email')
    assign = fields.Many2one('res.users', string='Assign To')
    mob = fields.Char(string='Contact Number')
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'),
                              ('done', 'Done'), ('closed', 'Closed')], default='draft', string='Status')

    def closed(self):
        self.end_date = fields.Date.today()
        self.state = 'closed'

    def start_work(self):
        self.state = 'pending'

    def done(self):
        self.state = 'done'


class HelpDeskKanban(models.Model):
    _name = 'help.desk.kanban'
    _inherit = 'help.desk'
    _description = 'Help Desk Kanban'

    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'),
                              ('done', 'Done'), ('closed', 'Closed')], default='draft', string='Status')
