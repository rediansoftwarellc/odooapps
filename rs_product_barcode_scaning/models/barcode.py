from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    barcode = fields.Text(string='Barcode')

    def action_add_products(self):
        barcodes = self.barcode.split('\n')
        for barcode in barcodes:
            barcode = barcode.strip()
            product = self.env['product.template'].search([('barcode', '=', barcode)], limit=1)
            if product:
                product_variant = product.product_variant_id
                line = self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': product_variant.id,
                    'product_uom_qty': 1.0,
                    'price_unit': product_variant.lst_price,
                })
                self.order_line += line
            else:
                raise ValueError('Product not found for barcode: %s' % barcode)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    barcode = fields.Text(string='Barcode')

    def action_add_products(self):
        barcodes = self.barcode.split('\n')
        for barcode in barcodes:
            barcode = barcode.strip()
            product = self.env['product.template'].search([('barcode', '=', barcode)], limit=1)
            if product:
                product_variant = product.product_variant_id
                line = self.env['purchase.order.line'].create({
                    'order_id': self.id,
                    'product_id': product_variant.id,
                    'product_qty': 1.0,
                    'price_unit': product_variant.lst_price,
                })
                self.order_line += line
            else:
                raise ValueError('Product not found for barcode: %s' % barcode)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    barcode = fields.Text(string='Barcode')

    def action_add_products(self):
        barcodes = self.barcode.split('\n')
        for barcode in barcodes:
            barcode = barcode.strip()
            product = self.env['product.template'].search([('barcode', '=', barcode)], limit=1)
            if product:
                product_variant = product.product_variant_id
                move = self.env['stock.move'].create({
                    'picking_id': self.id,
                    'product_id': product_variant.id,
                    'product_uom_qty': 1.0,
                    'product_uom': product_variant.uom_id.id,
                    'price_unit': product_variant.lst_price,
                    'name': product_variant.name,
                    'location_id': self.location_id.id,  # Set the location_id field
                    'location_dest_id': self.location_dest_id.id,  # Set the location_dest_id field
                })
                self.move_lines += move
            else:
                raise ValueError('Product not found for barcode: %s' % barcode)
