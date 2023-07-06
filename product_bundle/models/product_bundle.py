from odoo import fields, models, api, _
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)
            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty
            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            # Create products for bundles in stock.move
            product_template = line.product_id.product_tmpl_id
            if product_template:
                for vals in product_template.pack_product_ids:
                    procurements.append(self.env['procurement.group'].Procurement(
                        vals.product_id,
                        product_qty, procurement_uom,
                        line.order_id.partner_shipping_id.property_stock_customer,
                        line.product_id.display_name,
                        line.order_id.name,
                        line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is Product Pack', widget="boolean_toggle")
    tags = fields.Char(string='Product Tags')
    company = fields.Many2one('res.company', string='Company')
    calculate_price = fields.Boolean(string='Calculate Pack Price')
    pack_product_ids = fields.One2many('pack.product', 'template_id')
    pack_price = fields.Float(string="Pack Price", compute='_compute_pack_price', store=True)

    @api.depends('calculate_price', 'pack_product_ids', 'pack_product_ids.product_id', 'pack_product_ids.quantity')
    def _compute_pack_price(self):
        for vals in self:
            if vals.calculate_price == True:
                vals.pack_price = sum(val.quantity * val.product_id.lst_price for val in vals.pack_product_ids)
                vals.list_price = vals.pack_price
            else:
                vals.pack_price = 0.0

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_pack = fields.Boolean(string='Is Product Pack', widget="boolean_toggle")


class PackProduct(models.Model):
    _name = 'pack.product'
    _description = "Pack Product"

    template_id = fields.Many2one('product.template')
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float(string="Quantity")
    image = fields.Binary(string="Image")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _create_stock_moves(self, picking):
        stock_move = self.env['stock.move']
        for line in self.filtered(lambda l: not l.display_type):
            if line.product_id.is_pack:
                bundle_products = line.product_id.pack_product_ids.mapped('product_id')
            else:
                bundle_products = [line.product_id]
            for product in bundle_products:
                move_vals = line._prepare_stock_moves(picking)[0]
                move_vals['product_id'] = product.id
                move_vals['product_uom_qty'] = line.product_qty
                move_vals['product_uom'] = line.product_uom.id
                stock_move |= stock_move.create(move_vals)
        return stock_move


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_bundle_pack = fields.Boolean(string="Allow Bundle Pack on Purchase", default=False,
                                       help='Enable Bundle Pack feature on Purchase Orders.')

    def set_values(self):
        """type setting field values"""
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('product_bundle.allow_bundle_pack', self.allow_bundle_pack)
        return res

    def get_values(self):
        """type getting field values"""
        res = super(ResConfigSettings, self).get_values()
        value = self.env['ir.config_parameter'].sudo().get_param('product_bundle.allow_bundle_pack')
        res.update(allow_bundle_pack=bool(value))
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'