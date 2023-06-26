from odoo import fields, models, api, _
from datetime import datetime


# Inherit sale order module
# Code:- Keshav pal
class SaleOrder(models.Model):
    _inherit = "sale.order"

    c_datetime = fields.Datetime(string='Date and Time', readonly=True, tracking=True)


    # This function is used to cancel the all sale order
    def cancel_all_sale_order(self):
        for val in self:
            all_cancel = self.env['ir.config_parameter'].get_param('all_in_one_cancelation.operation_type')
            if all_cancel == 'cancel_only':
                stock_obj = self.env['stock.picking'].search([('origin', '=', val.name)])
                if stock_obj:
                    stock_obj.write({'state': 'cancel'})
                invoice_obj = self.env['account.move'].search([('invoice_origin', '=', val.name)])
                if invoice_obj:
                    invoice_obj.write({'state': 'cancel'})
                val.state = 'cancel'
                val.write({'state': 'cancel', 'c_datetime': datetime.now()})




    # This function used to cancel the sale order and set it to draft
    def cancel_and_draft_sale_order(self):
        for val in self:
            all_cancel = self.env['ir.config_parameter'].get_param('all_in_one_cancelation.operation_type')
            if all_cancel == 'cancel_reset_draft':
                stock_obj = self.env['stock.picking'].search([('origin', '=', val.name)])
                if stock_obj:
                    stock_obj.write({'state': 'cancel'})
                stock_obj.write({'state': 'draft'})
                invoice_obj = self.env['account.move'].search([('invoice_origin', '=', val.name)])
                if invoice_obj:
                    invoice_obj.write({'state': 'cancel'})
                invoice_obj.write({'state': 'draft'})
                val.state = 'draft'
                val.write({'state': 'draft', 'c_datetime': datetime.now()})




    
    def _action_cancel(self):
        all_cancel = self.env['ir.config_parameter'].get_param('all_in_one_cancelation.operation_type')
        if all_cancel == 'cancel_only':
            # inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
            # inv.button_cancel()
            stock_obj = self.env['stock.picking'].search([('origin', '=', self.name)])
            if stock_obj:
                stock_obj.write({'state': 'cancel'})
            invoice_obj = self.env['account.move'].search([('invoice_origin', '=', self.name)])
            if invoice_obj:
                invoice_obj.write({'state': 'cancel'})
                c_datetime = fields.Datetime.now()
            order_state = self.write({'state': 'cancel'})
            self.write({'state': 'cancel', 'c_datetime': datetime.now()})
        elif all_cancel == 'cancel_reset_draft':
            stock_obj = self.env['stock.picking'].search([('origin', '=', self.name)])
            if stock_obj:
                stock_obj.write({'state': 'cancel'})
            stock_obj.write({'state': 'draft'})
            invoice_obj = self.env['account.move'].search([('invoice_origin', '=', self.name)])
            if invoice_obj:
                invoice_obj.write({'state': 'cancel'})
            invoice_obj.write({'state': 'draft'})
            c_datetime = fields.Datetime.now()
            self.write({'c_datetime': c_datetime, 'state': 'draft'})
            order_state = self.write({'state': 'draft'})
        elif all_cancel == 'cancel_delete':
            order_state = self.write({'state': 'cancel'})
            stock_obj = self.env['stock.picking'].search([('origin', '=', self.name)])
            if stock_obj:
                stock_obj.write({'state': 'cancel'})
            stock_obj.unlink()
            invoice_obj = self.env['account.move'].search([('invoice_origin', '=', self.name)])
            if invoice_obj:
                invoice_obj.write({'state': 'cancel'})
        return order_state


# Created setting buttons
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    operation_type = fields.Selection([('cancel_only', 'Cancel Only'), ('cancel_delete', 'Cancel and Delete'),
                                       ('cancel_reset_draft', 'Cancel and Reset to Draft')])

    def set_values(self):
        """type setting field values"""
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('all_in_one_cancelation.operation_type', self.operation_type)
        return res

    def get_values(self):
        """type getting field values"""
        res = super(ResConfigSettings, self).get_values()
        value = self.env['ir.config_parameter'].sudo().get_param('all_in_one_cancelation.operation_type')
        res.update(operation_type=str(value))
        return res

# Inheriting purchase module
#Code:-Prabhat Shaw
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    c_datetime = fields.Datetime(string='Date and Time', readonly=True, tracking=True)


    # This function is used to cancel all purchase order
    def cancel_all_purchase_order(self):
        for val in self:
            all_cancel = self.env['ir.config_parameter'].get_param('all_in_one_cancelation.operation_type')
            if all_cancel == 'cancel_only':
                stock_obj = self.env['stock.picking'].search([('origin', '=', val.name)])
                if stock_obj:
                    stock_obj.write({'state': 'cancel'})
                invoice_obj = self.env['account.move'].search([('invoice_origin', '=', val.name)])
                if invoice_obj:
                    invoice_obj.write({'state': 'cancel'})
                val.state = 'cancel'
                val.write({'state': 'cancel', 'c_datetime': datetime.now()})


    #  This function is used to cancel the purchase order and set it to the draft
    def cancel_and_draft_purchase_order(self):
        for val in self:
            all_cancel = self.env['ir.config_parameter'].get_param('all_in_one_cancelation.operation_type')
            if all_cancel == 'cancel_reset_draft':
                stock_obj = self.env['stock.picking'].search([('origin', '=', val.name)])
                if stock_obj:
                    stock_obj.write({'state': 'cancel'})
                stock_obj.write({'state': 'draft'})
                invoice_obj = self.env['account.move'].search([('invoice_origin', '=', val.name)])
                if invoice_obj:
                    invoice_obj.write({'state': 'cancel'})
                invoice_obj.write({'state': 'draft'})
                val.state = 'draft'
                val.write({'state': 'draft', 'c_datetime': datetime.now()})


    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))
        self.write({'state': 'cancel', 'c_datetime': datetime.now(), 'mail_reminder_confirmed': False})


















