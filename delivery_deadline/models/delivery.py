from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    manufacturing_count = fields.Integer(string='Manufacturing')
    mrp_id = fields.Many2one('mrp.production', string='MRP')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        mrp_obj = self.env['mrp.production']
        for line in self.order_line:
            if line.product_id:
                bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                      ('type', '=', 'normal')])
                if bom_obj:
                    move_raw_ids = []
                    for bom_line in bom_obj.bom_line_ids:
                        prod_id = bom_line.product_id.id
                        prod_uom = bom_line.product_uom_id.id
                        line_dict = {'product_id': prod_id, 'name': mrp_obj.location_src_id, 'product_uom': prod_uom,
                                     'location_id': 8, 'location_dest_id': 8}
                        move_raw_ids.append((0, 0, line_dict))
                    mrp = mrp_obj.create({'product_id': line.product_id.id, 'product_qty': line.product_uom_qty,
                                         'product_uom_id': line.product_uom.id, 'order_id': self.id,
                                         'sale_order_line': self.order_line.id, 'move_raw_ids': move_raw_ids})
        self.manufacturing_count = len(mrp)
        self.mrp_id = mrp.id
        return res

    def view_mrp_action(self):
        self.ensure_one()
        view_id = self.env.ref('mrp.mrp_production_form_view').id
        context = self._context.copy()
        return {
            'type': 'ir.actions.act_window',
            'res_id': self.mrp_id.id,
            'name': _("Manufacturing"),
            'view_mode': 'form',
            'view_id': view_id,
            'context': context,
            'res_model': 'mrp.production',
            "target" : "self",
        }


class MrpProduction(models.Model):
    _inherit ='mrp.production'

    sale_order_line = fields.Many2one('sale.order.line', string='Sale Order Line')
    order_id = fields.Many2one('sale.order', string='Sale order')
    delivery_date = fields.Datetime(string='Delivery Date Scheduled', default=fields.Date.context_today)
    deadline_date = fields.Datetime(string='Delivery Deadline Date', default=fields.Date.context_today)


class StockPicking(models.Model):
    _inherit = 'stock.picking'


class StockMove(models.Model):
    _inherit = 'stock.move'

    delivery_date = fields.Datetime(string='Date Scheduled', default=fields.Date.context_today)
    deadline_date = fields.Datetime(string='Deadline', default=fields.Date.context_today)
    location_id = fields.Many2one('stock.location', string='From')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location')
