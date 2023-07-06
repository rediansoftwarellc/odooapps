from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    warranty_count = fields.Integer(string='Warranty', readonly=True)

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_('It is not allowed to confirm an order in the following states: %s') % (', '.join(self._get_forbidden_rstate_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        context = self._context.copy()
        context.pop('default_name', None)

        for val in self.order_line:
            if val.product_id:
                obj = self.env['product.template'].search([('id', '=', val.product_id.product_tmpl_id.id)])
                a = self.env['product.warranty'].create({'partner_id': self.partner_id.id, 'product': obj.id,
                                                         'order_id': self.id})
        self.warranty_count = len(a)
        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

    def check_warranty(self):
        view_id = self.env.ref('product_warranty.product_warranty_tree_view_id').id
        context = self._context.copy()
        return {
            'name': _('Product Warranty'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.warranty',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            # 'domain': [('order_id', '=', self.id)],
            'context': context,
            'target': 'self',
        }

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    serial_number = fields.Char(string="Serial Number")

    @api.onchange('product_id')
    def _onchange_product_serial(self):
        for val in self:
            if val.product_id:
                val.serial_number = val.product_id.serial_number

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    warranty_period = fields.Char(string='Warranty Period')
    allow_warranty_renewal_times = fields.Char(string='Allow Warranty Renewal Times')
    allow_renewal = fields.Boolean(string= 'Allow Renewal')
    warranty_renewal_periods = fields.Char(string='Warranty Renewal Periods')
    warranty_renewal_cost = fields.Float(string='Warranty Renewal Cost')
    under_warranty = fields.Boolean(string='Under Warranty')
    merchant = fields.Char(string='Merchant')
    serial_number = fields.Char(string='Serial Number')
    model = fields.Char(string='Model')
    create_warranty_sales_order = fields.Boolean(string="Create Warranty from sales order", default=True)
    take_warranty = fields.Boolean(string="Take warranty")


    @api.depends('warranty_period', 'warranty_renewal_periods', 'product_variant_ids.warranty_renewal_times')
    def _compute_under_warranty(self):
        for product in self:
            if product.warranty_period:
                under_warranty = False
                for variant in product.product_variant_ids:
                    if variant.warranty_renewal_times < product.allow_warranty_renewal_times:
                        if variant.warranty_period + variant.warranty_renewal_periods * product.warranty_renewal_periods >= variant._get_current_warranty_time():
                            under_warranty = True
                            break
                    else:
                        if variant.warranty_period >= variant._get_current_warranty_time():
                            under_warranty = True
                            break
                product.under_warranty = under_warranty

    # @api.onchange('create_warranty_sales_order')
    # def _onchnage_hide(self):
    #     print('*********')
    #     settings = self.env['warranty.setting'].search([('create_warranty_from_so', '=', True)])
    #     print('--------true', settings)
    #     if settings:
    #         print('----------')


    # @api.model
    # def create(self, vals):
    #     product_vals = {
    #         'warranty_period': vals.get('warranty_period'),
    #         'allow_warranty_renewal_times': vals.get('allow_warranty_renewal_times'),
    #         'allow_renewal': vals.get('allow_renewal'),
    #         'warranty_renewal_periods': vals.get('warranty_renewal_periods'),
    #         'warranty_renewal_cost': vals.get('warranty_renewal_cost'),
    #         'under_warranty': vals.get('under_warranty'),
    #     }
    #     product = super(ProductTemplate, self).create(vals)
    #     for variant in product.product_variant_ids:
    #         variant.write(product_vals)
    #     setting_obj = self.env['warranty.setting'].search([('create_warranty_from_so', '=', True)])
    #     if setting_obj:
    #         # vals['create_warranty_sales_order'] = True
    #         # vals['create_warranty_sales_order'].create({'create_warranty_from_so'})
    #     return product


class ProductProduct(models.Model):
    _inherit = 'product.product'


    warranty_period = fields.Char(string='Warranty Period')
    allow_warranty_renewal_times = fields.Char(string='Allow Warranty Renewal Times')
    allow_renewal = fields.Boolean(string= 'Allow Renewal')
    warranty_renewal_periods = fields.Char(string='Warranty Renewal Periods')
    warranty_renewal_cost = fields.Float(string='Warranty Renewal Cost')
    under_warranty = fields.Boolean(string='Under Warranty')
    take_warranty = fields.Boolean(string="Take warranty", default=True)