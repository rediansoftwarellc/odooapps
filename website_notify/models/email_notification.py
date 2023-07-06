from odoo import models, fields, api

class CustomerEmailNotification(models.Model):
    _name = "customer.email.notification"
    _description = "Customer Email Notification"

    name = fields.Char(string='Email')
    product_id = fields.Many2one('product.product')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get())
    p_url = fields.Char(string="URL", compute='get_url')

    def get_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        print('--------url-', base_url)
        for rec in self:
            url = base_url + '/shop/product/' + rec.product_id.name.lower().replace(' ', '-') + '-' + str(rec.product_id.id)
            rec.p_url = url
            print('-------p-irl-', rec.p_url)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self):
        print('----Done----')
        notify_obj = self.env['customer.email.notification']
        res = super(StockMove, self)._action_done()
        for rec in self:
            print('--rec--', rec)
            if rec.product_id.qty_available > 0:
                notify_ids = notify_obj.search([('product_id', '=', rec.product_id.id)])
                print("===========notify_ids>>>>>>>>>>",notify_ids)
                if notify_ids:
                    for notify in notify_ids:
                        print('--notify--', notify)
                        # Send Mail logic
                        # template = self.env.ref('website_notify.customer_email_template_product_notify')
                        # template.send_mail(notify.id, force_send=True)
                        # print('------template ID--', template)
                        # print('------send-', template)
                        notify.unlink()
        return res