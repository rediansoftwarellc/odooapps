from odoo import fields, models, _, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import date

class ProductWarranty(models.Model):
    _name = 'product.warranty'
    _description = 'product warranty'
    _rec_name = 'name'

    # FIELD OF THE SEQUENCE
    name = fields.Char(string='Receipt', copy=False, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    address = fields.Char(string='Address', related='partner_id.street', store=True)
    city = fields.Char(string='City', related='partner_id.city', store=True)
    state_id = fields.Char(string='State', related='partner_id.state_id.name', store=True)
    country = fields.Char(string='Country', related='partner_id.country_id.name', store=True)
    zip = fields.Char(string='Zip', related='partner_id.zip', store=True)
    number = fields.Char(string='Phone', related='partner_id.phone')
    email = fields.Char(string='Email', related='partner_id.email')
    warranty_team = fields.Many2one('warranty.team', string='Warranty team')
    tags = fields.Many2one('warranty.tags', string='Tags')
    sales_person = fields.Many2one('res.users', default=lambda self: self.env.user, readonly='1')
    product = fields.Many2one('product.template', string='Product', required=True)
    serial_no = fields.Char(string='Serial Number', related='product.serial_number', readonly='0')
    model = fields.Char(string='Model', related='product.model', store=True)
    merchant = fields.Char(string='Merchant', related='product.merchant', store=True)
    warranty_type = fields.Selection([('free', 'Free'), ('paid', 'Paid')], string='Warranty Type', default='free')
    warranty_start_date = fields.Date(string='Warranty Start Date', default=fields.Date.today())
    warranty_end_date = fields.Date(string='Warranty End Date', readonly='1', compute='_compute_warranty_end_date',
                                    store=True)
    no_of_renew = fields.Integer(string='No of Renew')
    state = fields.Selection([('new', 'NEW'),
                              ('under_warranty', 'UNDER WARRANTY'),
                              ('to_be_invoice', 'TO BE INVOICE'),
                              ('invoiced', 'INVOICED'),
                              ('to_be_renew', 'TO BE RENEW'),
                              ('expired', 'EXPIRED')], default='new')
    warranty_history = fields.One2many('warranty.history', 'warranty_id', string="Warranty History")
    claim_history = fields.One2many('claim.claim', 'warranty_id', string="Claim History")
    # invoice_ids = fields.One2many('account.move', 'warranty_id', string='Invoices')
    renewal_amount = fields.Float(string='Renewal Amount')
    order_id = fields.Many2one('sale.order', string='Order ID')

    @api.onchange('product')
    def _onchange_renewal_amount(self):
        if self.product:
            self.renewal_amount = self.product.warranty_renewal_cost

    def view_cost_centre_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_id': self.warranty_renew_id.id,
            'name': _("Warranty Renewal"),
            'view_mode': 'form',
            'res_model': 'warranty.renewal.wizard',
            "target" : "new",
        }

    @api.constrains('serial_no','product')
    def _check_serial_no_unique(self):
        for warranty in self:
            if self.search_count([('serial_no', '=', warranty.serial_no)]) > 1:
                raise ValidationError(_("You can not create more than one warranty with same '" + str(self.serial_no) + "' "
                                        "serial no. Please Renew existing warranty"))

    def button_action(self):
        lst = []
        for val in self:
            if val.warranty_type == 'paid':
                lst.append((0, 0, {'start_date': val.warranty_start_date, 'end_date': val.warranty_end_date,
                                   'warranty_id': val.id, 'warranty_type': val.warranty_type,
                                   'r_amount': val.renewal_amount}))
                val.warranty_history = lst
                val.state = 'to_be_invoice'
            else:
                # val.warranty_end_date = date.today()
                lst.append((0, 0, {'start_date': val.warranty_start_date, 'end_date': val.warranty_end_date,
                               'warranty_id': val.id, 'warranty_type': val.warranty_type}))
                val.warranty_history = lst
                val.state = 'under_warranty'

    def create_invoices(self):
        for val in self:
            if val.product:
                obj = self.env['product.product'].search([('product_tmpl_id', '=', val.product.id)])
                a = self.env['account.move'].create([
                    {
                        'invoice_date': fields.Date.context_today(self),
                        'invoice_date_due': fields.Date.context_today(self),
                        'partner_id': self.partner_id.id,
                        'move_type': 'out_invoice',
                        'receipt': self.name,
                        'state': 'draft',
                        'invoice_line_ids': [
                            (0, 0, {
                                'product_id': obj.id,
                                'name': obj.name,
                                'quantity': 1.00,
                                'price_unit': val.renewal_amount,
                                'price_subtotal': val.renewal_amount,
                            }),
                        ],
                    },
                ])
                return {
                    'name': _('Customer Invoice'),
                    'view_mode': 'form',
                    'view_id': self.env.ref('account.view_move_form').id,
                    'res_model': 'account.move',
                    'context': "{'default_move_type': 'out_invoice', 'move_type':'out_invoice', 'journal_type': 'sale'}",
                    'type': 'ir.actions.act_window',
                    'res_id': a.id,
                    'target': 'self',
                }

    @api.model
    def create(self, vals):
        # SEQUENCE GENERATOR OF THE ORDER ID
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('prod.seq')
        r = super(ProductWarranty, self).create(vals)
        return r

    @api.depends('tags')
    def _compute_warranty_end_date(self):
        for record in self:
            if record.tags.name == '6 Months':
                record.warranty_end_date = (fields.Date.today() + relativedelta(months=+6)).strftime('%Y-%m-%d')
            elif record.tags.name == '1 Year':
                record.warranty_end_date = (fields.Date.today() + relativedelta(months=+12)).strftime('%Y-%m-%d')
            else:
                record.warranty_end_date = False


class ClaimHistory(models.Model):
    _name = "claim.claim"

    name = fields.Char(string='Claim Subject')
    claim_date = fields.Datetime(string='Claim Date')
    partner = fields.Char(string='Customer')
    product = fields.Char(string='Product')
    serial_no = fields.Char(string='Serial number')
    warranty_id = fields.Many2one('product.warranty', string='Product Warranty')
    state = fields.Selection([('new', 'NEW'), ('under_maintenance', 'UNDER MAINTENANCE'),
                              ('ready_to_deliver', 'READY TO DELIVER'), ('done', 'Done')], string='Status')


class AccountMove(models.Model):
    _inherit = "account.move"

    receipt = fields.Char(string='Warranty')

    def action_post(self):
        self._post(soft=False)
        warranty_obj = self.env['product.warranty'].search([('name', '=', self.receipt)])
        if warranty_obj:
            warranty_obj.write({'state': 'under_warranty'})
        return False


class Claim(models.Model):
    _name = "warranty.claims"
    _description = "Warranty Claims"

    name = fields.Char(string='Claim Subject')
    claim_date = fields.Datetime(string='Claim Date')
    responsible = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user)
    priority = fields.Selection([('normal', 'Normal'), ('high', 'High')], copy=False, default='normal', required=True)
    sales_team = fields.Many2one('warranty.team', string='Sales Team')
    deadline = fields.Date(string='Deadline')
    partner_id = fields.Many2one('res.partner', string='Customer')
    phone = fields.Char(string='Phone', related='partner_id.phone')
    email = fields.Char(string='Email', related='partner_id.email')
    product_id = fields.Many2one('product.template', string='Product')
    serial_no = fields.Char(string='Serial number', related='product_id.serial_number')
    trouble_responsible = fields.Char(string='Trouble Responsible')
    category = fields.Many2one('category', string='Category')
    description = fields.Text()
    state = fields.Selection([('new', 'NEW'), ('under_maintenance', 'UNDER MAINTENANCE'),
                              ('ready_to_deliver', 'READY TO DELIVER'), ('done', 'Done')], string='Status')

    def submit_claim(self):
        lst = []
        warranty_obj = self.env['product.warranty'].search([('partner_id', '=', self.partner_id.id),
                                                            ('serial_no', '=', self.serial_no)])
        if warranty_obj:
            if warranty_obj.warranty_type == 'paid':
                self.write({'state': 'under_maintenance'})
                lst.append((0, 0, {'name': self.name, 'claim_date': self.claim_date, 'partner': self.partner_id.name,
                                   'product': self.product_id.name, 'serial_no': self.serial_no, 'state': self.state,
                                   'warranty_id': warranty_obj.id}))
                warranty_obj.claim_history = lst


class ProductTemplate(models.Model):
    _inherit = "product.template"


class WarrantyRenewal(models.Model):
    _name = "warranty.renewal.wizard"
    _description = "Warranty Renewal"

    product_id = fields.Many2one("product.template", string="Product")
    serial_no = fields.Char(string='Serial No.')
    partner_id = fields.Many2one("res.partner", string="Customer")
    renewal_amount = fields.Float(string="Renewal Amount")
    warranty_id = fields.Many2one('product.warranty', string='Warranty')

    @api.onchange('product_id')
    def _onchange_serial_no(self):
        if self.product_id:
            self.serial_no = self.product_id.serial_number

    def renew_warranty(self):
        lst = []
        if self.partner_id == self.warranty_id.partner_id:
            warranty_obj = self.env['product.warranty'].search([('id', '=', self.warranty_id.id)])
            if warranty_obj:
                if warranty_obj.state == 'expired':
                    if warranty_obj.warranty_type == 'paid':
                        warranty_obj.renewal_amount = self.renewal_amount
                        lst.append((0, 0, {'start_date': warranty_obj.warranty_start_date,
                                           'end_date': warranty_obj.warranty_end_date,
                                           'warranty_id': warranty_obj.id,
                                           'r_amount': warranty_obj.renewal_amount,
                                           'warranty_type': warranty_obj.warranty_type}))
                        warranty_obj.warranty_history = lst
                else:
                    raise ValidationError(_("Product expire date is not finished"))
        else:
            raise ValidationError(_("Partner is not matching with this ['"+ str(self.product_id.name) +"'] product"))