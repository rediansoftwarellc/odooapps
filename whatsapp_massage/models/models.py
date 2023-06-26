from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id},
                }
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'message':'Hello Krishna',
                'context': {'default_user_id': self.id,'default_message':self.name + "is Available and price is "+ str(self.list_price) + '/n' + " Now you can Buy Thanks from your company name "}
                }

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def whatsapp_send_msg(self):
        if self.partner_id.mobile:
            message = f"Hello Your Order No: {self.name} Amounting {self.amount_total} Has Been Confirmed ThankYou For your trust! Do Not Hasistet to contact us If you have any questions"
            message_string = ''
            message = message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone="+self.partner_id.mobile+"&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }
class AccountMove(models.Model):
    _inherit = 'account.move'

    def whatsapp_send_invoice_msg(self):
        if self.partner_id.mobile:
            message = f"Hello {self.partner_id.name}, Your Invoice no : {self.name} Amounting {self.amount_total}  from  {self.company_id.name} This invoice is already paid,  Do Not Hasistet to contact us If you have any questions"
            message_string = ''
            message = message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone="+self.partner_id.mobile+"&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }