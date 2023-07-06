# subscription/models/subscription.py

from odoo import models, fields, api
from datetime import datetime, timedelta
import calendar

class Subscription(models.Model):
    _name = 'subscription.subscription'
    _description = 'Subscription'

    start_date = fields.Date(string='Start Date', required=True)
    duration = fields.Selection([('1', '1 month'), ('3', '3 months'), ('6', '6 months'), ('12', '1 year')],
                                string='Duration', required=True)
    subscription_lines = fields.One2many('subscription.subscription.line', 'subscription_id', string='Subscription Lines')

    @api.onchange('start_date', 'duration')
    def _onchange_start_date_duration(self):
        if self.start_date and self.duration:
            # self.subscription_lines = [(5, 0, 0)]  # Clear existing lines
            duration = int(self.duration)
            end_date = datetime.strptime(str(self.start_date), '%Y-%m-%d')
            print('---end-date---', end_date)
            for i in range(duration):
                print('--i--', i)
                line_vals = {
                    'start_date': end_date.strftime('%Y-%m-%d'),
                    'end_date': (end_date + timedelta(days=calendar.monthrange(end_date.year, end_date.month)[1] - 1)).strftime('%Y-%m-%d'),
                }
                print('--disc--', line_vals)
                self.subscription_lines = [(0, 0, line_vals)]
                print('-lines-', self.subscription_lines)
                end_date = end_date + timedelta(days=calendar.monthrange(end_date.year, end_date.month)[1])
                print('--end--', end_date)


class SubscriptionLine(models.Model):
    _name = 'subscription.subscription.line'
    _description = 'Subscription Line'

    subscription_id = fields.Many2one('subscription.subscription', string='Subscription')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')





# # subscription/models/subscription.py
#
# from odoo import models, fields, api
# from datetime import datetime, timedelta
# import calendar
#
# class Subscription(models.Model):
#     _name = 'subscription.subscription'
#     _description = 'Subscription'
#
#     start_date = fields.Date(string='Start Date', required=True)
#     duration = fields.Selection([
#         ('1', '1 month'),
#         ('3', '3 months'),
#         ('6', '6 months'),
#         ('12', '1 year')
#     ], string='Duration', required=True)
#     subscription_lines = fields.One2many('subscription.subscription.line', 'subscription_id', string='Subscription Lines')
#
#     @api.onchange('start_date', 'duration')
#     def _onchange_start_date_duration(self):
#         if self.start_date and self.duration:
#             self.subscription_lines = [(5, 0, 0)]  # Clear existing lines
#             duration = int(self.duration)
#             end_date = datetime.strptime(str(self.start_date), '%Y-%m-%d')
#             for i in range(duration):
#                 line_vals = {
#                     'start_date': (end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
#                     'end_date': (end_date + timedelta(days=calendar.monthrange(end_date.year, end_date.month)[1])).strftime('%Y-%m-%d'),
#                 }
#                 self.subscription_lines = [(0, 0, line_vals)]
#                 end_date = end_date + timedelta(days=calendar.monthrange(end_date.year, end_date.month)[1])
#
# class SubscriptionLine(models.Model):
#     _name = 'subscription.subscription.line'
#     _description = 'Subscription Line'
#
#     subscription_id = fields.Many2one('subscription.subscription', string='Subscription')
#     start_date = fields.Date(string='Start Date')
#     end_date = fields.Date(string='End Date')




# # subscription/models/subscription.py
#
# from odoo import models, fields, api
# from datetime import datetime, timedelta
#
# class Subscription(models.Model):
#     _name = 'subscription.subscription'
#     _description = 'Subscription'
#
#     start_date = fields.Date(string='Start Date',default='', required=True)
#     duration = fields.Selection([
#         ('1', '1 month'),
#         ('3', '3 months'),
#         ('6', '6 months'),
#         ('12', '1 year')
#     ], string='Duration', required=True)
#     subscription_lines = fields.One2many('subscription.subscription.line', 'subscription_id', string='Subscription Lines')
#
#     @api.onchange('start_date', 'duration')
#     def _onchange_start_date_duration(self):
#         if self.start_date and self.duration:
#             self.subscription_lines = [(5, 0, 0)]  # Clear existing lines
#             duration = int(self.duration)
#             end_date = datetime.strptime(str(self.start_date), '%Y-%m-%d')
#             for i in range(duration):
#                 line_vals = {
#                     'start_date': end_date.strftime('%Y-%m-%d'),
#                     'end_date': (end_date + timedelta(days=30)).strftime('%Y-%m-%d'),
#                 }
#                 self.subscription_lines = [(0, 0, line_vals)]
#                 end_date += timedelta(days=30)
#
# class SubscriptionLine(models.Model):
#     _name = 'subscription.subscription.line'
#     _description = 'Subscription Line'
#
#     subscription_id = fields.Many2one('subscription.subscription', string='Subscription')
#     start_date = fields.Date(string='Start Date')
#     end_date = fields.Date(string='End Date')
