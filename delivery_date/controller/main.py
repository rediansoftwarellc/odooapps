from odoo import http, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from datetime import datetime,timedelta
import pytz


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/deliverydate'], type='json', auth="public")
    def get_del_date(self, **post):
        print("post.................",post)
        not_display_timeslot = []
        not_display_timeslot2 = []
        all_time_slots = []
        all_records = []
        conf_obj = request.env['delivery.timeslot.config']
        day_obj = request.env['disable.timeslot.byday']
        date_obj = request.env['disable.timeslot.bydate']
        setting_obj = request.env['delivery.timeslot.setting']

        set_ids = setting_obj.search([])
        if set_ids:
            setting_obj = set_ids[0]
            # print" setting_obj===>",setting_obj

            display_timeslot_list = setting_obj.timeslot_ids.ids
            # print" display_timeslot_list",display_timeslot_list
            #        all_time_slots.extend[display_timeslot_list]

            #       check for day
            post.get('b_date')
            s = datetime.strptime(post.get('b_date'), '%Y-%m-%d')
            days = s.weekday()
            # print "days====",days
            day_ids = day_obj.search([('d_day', '=', days), ('day_id', '=', setting_obj.id)])
            # print "day_ids=========>",day_ids
            for t in day_ids:
                f = [i.id for i in t.dis_timeslots_ids]
                not_display_timeslot.extend(f)
                # print '==day====>',not_display_timeslot
            #       check for date
            post.get('b_date')
            t = datetime.strptime(post.get('b_date'), '%Y-%m-%d')
            # print"date===>",t
            date_ids = date_obj.search(
                [('disable_on_date', '=', post.get('b_date')), ('dis_date_id', '=', setting_obj.id)])
            # print"date_ids====?>",date_ids
            for v in date_ids:
                g = [j.id for j in v.dis_timeslot_ids]
                not_display_timeslot.extend(g)

            display_time_slot = set(display_timeslot_list) - set(not_display_timeslot)
            # print"kkkk================>>>>>",display_time_slot
            res = []
            for rec in conf_obj.browse(display_time_slot):
                # print"rec====",rec
                res.append({
                    'key': str(rec.id),
                    'value': str(rec.time_from) + ' - ' + str(rec.time_to)
                })
                # print "====>",res
            return res

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, request, **post):
        print("==controller==",post)
        config = request.env['ir.config_parameter']
        disable_date = config.get_param('cust.disable_date'),
        disable_comment = config.get_param('cust.disable_comment'),
        SaleOrder = request.env['sale.order']
        order = request.website.sale_get_order()

        # print "======disable_date===>",disable_date
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        shipping_partner_id = False
        if order:
            if order.partner_shipping_id.id:
                shipping_partner_id = order.partner_shipping_id.id
            else:
                shipping_partner_id = order.partner_invoice_id.id

        if disable_date[0] == 'True':
            d_date = 'none'
        else:
            d_date = 'block'

        if disable_comment[0] == 'True':
            d_cmt = 'none'
        else:
            d_cmt = 'block'

        render_values = {
            'website_sale_order': order,
            #             'disable_date': disable_date,
            #             'disable_comment': disable_comment,
        }
        # print"website_sale_order====",render_values.get('website_sale_order')
        # print'values=========',render_values

        render_values = self._get_shop_payment_values(order, **post)
        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        render_values.update({
            'disable_date': d_date,
            'disable_comment': d_cmt,
        })
        # print'values=========',render_values
        return request.render("website_sale.payment", render_values)

    @http.route(['/shop/add_delivery_to_sale_order'], type='json', auth="public")
    def add_delivery_to_sale_order(self, **post):
        print("post.................", post)
        sale_obj = request.env['sale.order']
        sobj = sale_obj.sudo().browse(int(post.get('order')))
        print("===sobj==>",sobj)
        time = post.get('time').split('-')
        print("===time===>",time)
        d = post.get('delivery_date') + ' ' + str(int(float(time[0].strip()))) + ':00:00'
        print(d)
        d_utc = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
        user_time_zone = pytz.timezone(request.env.user.partner_id.tz)
        print("==========user_time_zone========>", user_time_zone)
        tz_name = request.env.context.get('tz') or request.env.user.tz
        print("---tz-na",tz_name)
        today_utc = pytz.timezone('UTC').localize(d_utc, is_dst=False)
        print("====today_utc=======>",today_utc)
        sdate_dt = today_utc.astimezone(pytz.timezone(tz_name))
        print("====sdate_dt===========>",sdate_dt)
        sobj.sudo().write({'delivery_date': d, 'time_slots': post.get('time')})
        return True

    @http.route(['/shop/add_comment_to_sale_order'], type='json', auth="public")
    def add_comment_to_sale_order(self, **post):
        print("post.................",post)
        sale_obj = request.env['sale.order']
        so_obj = sale_obj.sudo().browse(int(post.get('order')))
        print('-----------obj', so_obj)
        so_obj.sudo().write({"comment": post.get("comment")})
        return True