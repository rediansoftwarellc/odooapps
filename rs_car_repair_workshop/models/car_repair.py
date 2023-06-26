from odoo import models,fields,api,_

class CarRepair(models.Model):
      _name='car.repair'
      _description='This model is used to maintain the recprds of car repair services'
      _rec_name='subject'

      ref=fields.Char('Reference', readonly=1,default=lambda self: _('New'))
      subject=fields.Char("Subject")
      assigned_to=fields.Many2one('res.users','Assigned To')
      priority=fields.Selection([('high','High'),
                                 ('normal','Normal'),
                                 ('low','Low')],'Priority')
      date_of_reciept=fields.Date('Date of Reciept')
      client=fields.Many2one('res.partner','Client')
      phone_no=fields.Integer('Phone No.')
      email_id=fields.Char('Email')
      mobile_no=fields.Integer('Mobile No.')
      address=fields.Char()
      pincode=fields.Char()
      state=fields.Char()
      country=fields.Char()
      checklist_line=fields.One2many('checklist.line','line1')
      car_info_line=fields.One2many('car.info.line','info')
      repair_status=fields.Selection([('recieved','Recieved'),
                                      ('in diagnosis','In Diagnosis'),
                                      ('quatation','Quatation'),
                                      ('approve quatation','Quatation Approved'),
                                      ('work_in_progress','Work In Progress'),
                                      ('done','Done')],default='recieved')
      diagnosis_count=fields.Integer(compute='compute_diagnosis')


      @api.model
      def create(self, vals):
          if vals.get('ref', _('New') == _('New')):
              vals['ref'] = self.env['ir.sequence'].next_by_code('car.repair')
          return super(CarRepair, self).create(vals)
      def create_diagnosis(self):
          for line in self.car_info_line:
              dict = {
                  'repair_ref':self.ref,
                  'subject1':self.subject,
                  'priority1':self.priority,
                  'date_of_reciept1':self.date_of_reciept,
                  'client1':self.client.id,
                  'phone_no1':self.phone_no,
                  'email_id1':self.email_id,
                  'mobile_no1':self.mobile_no,
                  'address1':self.address,
                  'pincode1':self.pincode,
                  'state1':self.state,
                  'country1':self.country,
                  'fleet_info_line': [(0, 0, {
                     'car1':line.car.id,
                      'model1':line.model.id,
                      'license_plate1':line.license_plate,
                      'chassis_no1':line.chassis_no,
                      'fuel_type1':line.fuel_type,
                      'service_nature1':line.service_nature,
                      'under_guarantee1':line.under_guarantee,
                      'gaurantee_type1':line.gaurantee_type
                  })]}
              self.env['car.diagnosis'].create(dict)
          # print('uuuuuuuuuuu',self.subject)
          self.repair_status='in diagnosis'
      def compute_diagnosis(self):
          self.diagnosis_count=self.env['car.diagnosis'].search_count([('repair_ref', '=', self.ref)])
      def get_diagnosis(self):
          return {
              'type': 'ir.actions.act_window',
              'name':'Car Diagnosis',
              'view_type':'form',
              'view_mode':'tree,form',
              'res_model': 'car.diagnosis',
              'domain': [('repair_ref', '=', self.ref)]
          }

      # def action_view_invoice(self):
      #     invoices = self.mapped('invoice_ids')
      #     action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
      #     if len(invoices) > 1:
      #         action['domain'] = [('id', 'in', invoices.ids)]
      #     elif len(invoices) == 1:
      #         form_view = [(self.env.ref('account.view_move_form').id, 'form')]
      #         if 'views' in action:
      #             action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
      #         else:
      #             action['views'] = form_view
      #         action['res_id'] = invoices.id
      #     else:
      #         action = {'type': 'ir.actions.act_window_close'}
      #
      #     context = {
      #         'default_move_type': 'out_invoice',
      #     }
      #     if len(self) == 1:
      #         context.update({
      #             'default_partner_id': self.partner_id.id,
      #             'default_partner_shipping_id': self.partner_shipping_id.id,
      #             'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
      #                                                self.env['account.move'].default_get(
      #                                                    ['invoice_payment_term_id']).get('invoice_payment_term_id'),
      #             'default_invoice_origin': self.name,
      #             'default_user_id': self.user_id.id,
      #         })
      #     action['context'] = context
      #     return action
class CarrpaLine(models.Model):
      _name='checklist.line'

      line1=fields.Many2one('car.repair',readonly=1)
      name=fields.Many2one('car.checklist','Checklist Name')
      created_by1=fields.Many2one('res.users','Created By',related='name.created_by')

class CarInfo(models.Model):
      _name='car.info.line'
      _description='We can see our car info here'

      info=fields.Many2one('car.repair',invisible=1)
      car=fields.Many2one('fleet.vehicle','Car')
      model=fields.Many2one('fleet.vehicle.model','Model')
      license_plate=fields.Char('License Plate')
      chassis_no=fields.Char('Chassis No')
      fuel_type=fields.Selection([('diesel','Diesel'),
                                  ('petrol','Petrol'),
                                  ('lpg','LPG'),('gasoline','Gasoline'),('hybrid','Hybrid')],string='Fuel Type')
      service_details=fields.Text('Servise Details')
      service_nature=fields.Selection([('full_service','Full Service')],string='Nature of Services')
      under_guarantee=fields.Selection([('yes','Yes'),
                                        ('no','No')],string='Under Guarantee')
      gaurantee_type=fields.Selection([('paid','Paid'),
                                       ('free','Free')],string='Gaurantee Type')


      @api.onchange('car')
      def onchange_car(self):
          if self.car:
              self.model=self.car.model_id.id
              self.license_plate=self.car.license_plate
              self.chassis_no=self.car.vin_sn
              self.fuel_type=self.car.fuel_type


