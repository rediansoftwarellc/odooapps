from odoo import models,fields,api,_
import datetime
class WorkOrder(models.Model):
      _name='work.order'
      _description='Work orders store here'
      _rec_name='work_order'

      work_order=fields.Char('Work Order')
      date=fields.Date('Date',default=datetime.date.today())
      priority_w=fields.Char('Priority')
      client_w=fields.Many2one('res.partner','Client')
      scheduled_dt=fields.Date('Scheduled Date')
      planned_end_dt=fields.Date(' Planned End Date')
      no_of_hr=fields.Float('Number of Hours')
      start_dt=fields.Datetime(' Start Date')
      end_dt=fields.Datetime('End Date')
      duration=fields.Float('Duration')
      hr_worked=fields.Float('Hours Worked')
      work_line=fields.One2many('work.line.info','work1')
      work_status=fields.Selection([('draft1','Draft'),
                                    ('pending','Pending'),
                                    ('in_progress1','In Progress'),
                                    ('finished','Finished'),('cancelled','Cancelled')],default='draft1')
      repair_origin1=fields.Char('Repair Ref')
      repair_order_count1 = fields.Char('Repair Order', compute='compute_repair_order1')
      quatation_count1 = fields.Integer(compute='compute_quatation1')
      diagnosis_count1 = fields.Integer(compute='compute_diagnosis1')
      assigned_to1=fields.Many2one('res.users','Assigned_to')
      def work_start(self):
          self.work_status='in_progress1'
          self.start_dt=datetime.date.today()
          self.env['car.repair'].search([('ref', '=', self.repair_origin1)]).update(
              {'repair_status': 'work_in_progress'})

      def work_stop(self):
          self.work_status='finished'
          self.end_dt=datetime.date.today()
          self.env['car.repair'].search([('ref', '=', self.repair_origin1)]).update(
              {'repair_status': 'done'})
      def work_pending(self):
          self.work_status='pending'
      def work_resume(self):
          self.work_status='in_progress1'
      def cancel(self):
          self.work_status='cancelled'

      def compute_repair_order1(self):
          self.repair_order_count1 = self.env['car.repair'].search_count([('ref', '=', self.repair_origin1)])

      def get_repair_order1(self):
          return {
              'type': 'ir.actions.act_window',
              'name': 'Repair Order',
              'view_type': 'form',
              'view_mode': 'tree,form',
              'res_model': 'car.repair',
              'domain': [('ref', '=', self.repair_origin1)]
          }

      def compute_quatation1(self):
          self.quatation_count1 = self.env['sale.order'].search_count([('car_repair_origin', '=', self.repair_origin1)])

      def get_quatation1(self):
          return {
              'type': 'ir.actions.act_window',
              'name': 'Sale',
              'view_type': 'form',
              'view_mode': 'tree,form',
              'res_model': 'sale.order',
              'domain': [('car_repair_origin', '=', self.repair_origin1)]
          }

      def compute_diagnosis1(self):
          self.diagnosis_count1 = self.env['car.diagnosis'].search_count([('repair_ref', '=', self.repair_origin1)])

      def get_diagnosis1(self):
          return {
              'type': 'ir.actions.act_window',
              'name': 'Car Diagnosis',
              'view_type': 'form',
              'view_mode': 'tree,form',
              'res_model': 'car.diagnosis',
              'domain': [('repair_ref', '=', self.repair_origin1)]
          }

class WorkLine(models.Model):
      _name='work.line.info'

      work1=fields.Many2one('work.order')
      car3=fields.Many2one('fleet.vehicle','Car')
      model3=fields.Many2one('fleet.vehicle.model','Model')
      license_plate3=fields.Char('License Plate')
      chassis_no3=fields.Char('Chassis No')
      fuel_type3=fields.Selection([('diesel','Diesel'),
                                  ('petrol','Petrol'),
                                  ('cng','CNG')],string='Fuel Type')
      service_details3=fields.Text('Servise Details')
      service_nature3=fields.Selection([('full_service','Full Service')],string='Nature of Services')
      under_guarantee3=fields.Selection([('yes','Yes'),
                                        ('no','No')],string='Under Guarantee')
      gaurantee_type3=fields.Selection([('paid','Paid'),
                                       ('free','Free')],string='Gaurantee Type')
      diagnosis_result_line=fields.One2many('product.line','spare_part1')

class SparePart1(models.Model):
    _name = 'product.line'

    spare_part1 = fields.Many2one('work.line.info')
    spare_product1 = fields.Many2one('product.product', 'Product')
    spare_quantity1 = fields.Integer('Quantity')
    spare_unit_price1 = fields.Float('Unit Price', digit=(4, 2))

    @api.onchange('spare_product1')
    def update_price(self):
        if self.spare_product:
            self.spare_unit_price1 = self.spare_product1.lst_price

