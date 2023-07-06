# from odoo.addons.website_sale.controllers.main import WebsiteSale
# from odoo.http import request
# from odoo import http, tools, _
#
# class WebsiteSale(WebsiteSale):
#     @http.route(['/shop/notifybyemail'], type='json', auth="public")
#     def get_unit_price(self, **post):
#         print('========post.get(product)==========>',post.get('product'))
#         obj = request.env['customer.email.notification']
#         c_ids = obj.sudo().search([('product_id', '=', int(post.get('product'))), ('name', '=', post.get('email'))])
#         print("c_________ids==>",c_ids)
#         if not c_ids:
#             obj.sudo().create({
#                 'product_id': int(post.get('product')),
#                 'name': post.get('email')
#             })
#         return {}

# from odoo import http
# from odoo.http import request


# class WebsiteSale(http.Controller):
#     @http.route(['/shop/product/<model("product.template"):product>'], type="http", auth="public", website="True")
#     def create_notify_mail(self, **kw):
#         print('******************')
#         mail_notification = request.env['customer.email.notification'].sudo().create(kw)
#         print('mmmmmmmmm', mail_notification)
#         return request.render("website_notify.thank", {
#             'name': mail_notification.name,
#             'product_id': mail_notification.product_id,
#         })

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL

class WebsiteSale(WebsiteSale):
    @http.route(['/shop/notifybyemail'], type='json', auth="public")
    def get_unit_price(self, **post):
        print('========post.get(product)==========>',post.get('product'))
        obj = request.env['customer.email.notification']
        c_ids = obj.sudo().search([('product_id', '=', int(post.get('product'))), ('name', '=', post.get('email'))])
        if not c_ids:
            obj.sudo().create({
                'product_id': int(post.get('product')),
                'name': post.get('email')
            })
        return {}