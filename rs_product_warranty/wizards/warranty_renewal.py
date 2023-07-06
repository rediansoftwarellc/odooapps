from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class WarrantyRenewal(models.TransientModel):
    _name = "warranty.renewal"
    _description = "Warranty Renewal"

    product_id = fields.Many2one("product.template", string="Product")
    serial_no = fields.Char(string='Serial No.')
    partner_id = fields.Many2one("res.partner", string="Customer")
    renewal_amount = fields.Float(string="Renewal Amount")
    warranty_id = fields.Many2one('product.warranty', string='Warranty')

    @api.onchange('product_id')
    def _onchange_serial_no(self):
        for val in self:
            if val.product_id:
                val.serial_no = val.product_id.serial_number

    @api.model
    def default_get(self, fields):
        res = super(WarrantyRenewal, self).default_get(fields)
        res['warranty_id'] = self.env.context.get('active_id')
        return res

    def renew_warranty(self):
        lst = []
        if self.product_id == self.warranty_id.product and self.partner_id == self.warranty_id.partner_id:
            if self.warranty_id.state == 'expired':
                if self.warranty_id.warranty_type == 'paid':
                    self.warranty_id.renewal_amount = self.renewal_amount
                    lst.append((0, 0, {'start_date': self.warranty_id.warranty_start_date,
                                       'end_date': self.warranty_id.warranty_end_date,
                                       'warranty_id': self.warranty_id.id, 'r_amount': self.warranty_id.renewal_amount,
                                       'warranty_type': self.warranty_id.warranty_type}))
                    self.warranty_id.warranty_history = lst
            else:
                raise ValidationError(_("Product expire date is not finished"))
        else:
            raise ValidationError(_("Partner is not matching with this ['"+ str(self.product_id.name) +"'] product"))