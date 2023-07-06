from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_date = fields.Date(string="Delivery Date")
    comment = fields.Text(string="Customer Comment")
    time_slots = fields.Char(string="TimeSlots")
    is_config = fields.Boolean(string="Config", default='config_check')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for stock_id in self.picking_ids:
            if self.delivery_date:
                stock_id.write({'scheduled_date': self.delivery_date, 'delivery_time_slots': self.time_slots})
        return res

    def config_check(self):
        delivery_date = self.env['ir.config_parameter'].get_param('delivery_date.delivery_date')
        disable_comment = self.env['ir.config_parameter'].get_param('delivery_date.disable_comment')
        if delivery_date and disable_comment:
            return True
        else:
            return False

class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_time_slots = fields.Char(string="Delivery Time")