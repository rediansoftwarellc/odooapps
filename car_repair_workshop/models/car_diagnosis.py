from odoo import models, fields, api, _


class CarDiagnosis(models.Model):
    _name = 'car.diagnosis'
    _description = 'These model will store data about car diagnosis'
    _rec_name = 'subject1'

    refe = fields.Char('Reference', readonly=1, default=lambda self: _('New'))
    subject1 = fields.Char("Subject")
    technician = fields.Many2one('res.users', 'Technician')
    priority1 = fields.Selection([('high', 'High'),
                                  ('normal', 'Normal'),
                                  ('low', 'Low')], 'Priority')
    date_of_reciept1 = fields.Date('Date of Reciept')
    client1 = fields.Many2one('res.partner', 'Client')
    phone_no1 = fields.Integer('Phone No.')
    email_id1 = fields.Char('Email')
    mobile_no1 = fields.Integer('Mobile No.')
    address1 = fields.Char()
    pincode1 = fields.Char()
    state1 = fields.Char()
    country1 = fields.Char()
    diagnosis_status = fields.Selection([('draft', 'Draft'),
                                         ('in_progress', 'In Progress'),
                                         ('done', 'Done')], string='Status', default='draft', readonly=True)
    fleet_info_line = fields.One2many('fleet.info.line', 'info1')
    repair_ref = fields.Char('Car Repair Ref')
    quatation_count = fields.Integer(compute='compute_quatation')

    @api.model
    def create(self, vals):
        if vals.get('refe', _('New') == _('New')):
            vals['refe'] = self.env['ir.sequence'].next_by_code('car.diagnosis')
        return super(CarDiagnosis, self).create(vals)

    def assign_tech(self):
        return self.env['ir.actions.act_window']._for_xml_id("car_repair_workshop.assign_technician_wizard_action")

    def create_quatation(self):
        for line in self.fleet_info_line:
            for n in range(len(line)):
                for mine in line.product_line:
                    dict = {
                        'car_repair_origin': self.repair_ref,
                        'partner_id': self.client1.id,
                        'order_line': [(0, 0, {
                            'model': line.model1.id,
                            'license_plate': line.license_plate1,
                            'product_id': mine.spare_product.id,
                            'product_uom_qty':mine.spare_quantity
                        })]}
                    print(dict)
                    self.env['sale.order'].create(dict)
        self.diagnosis_status = 'done'
        self.env['car.repair'].search([('ref', '=', self.repair_ref)]).update(
            {'repair_status': 'quatation'})

    def compute_quatation(self):
        self.quatation_count = self.env['sale.order'].search_count([('car_repair_origin', '=', self.repair_ref)])

    def get_quatation(self):
        return{
              'type': 'ir.actions.act_window',
              'name':'Sale',
              'view_type':'form',
              'view_mode':'tree,form',
              'res_model': 'sale.order',
              'domain': [('car_repair_origin', '=', self.repair_ref)]
          }


class FleetInfo(models.Model):
    _name = 'fleet.info.line'
    _description = 'We can see our car info here'

    info1 = fields.Many2one('car.diagnosis', invisible=1)
    car1 = fields.Many2one('fleet.vehicle', 'Car')
    model1 = fields.Many2one('fleet.vehicle.model', 'Model')
    license_plate1 = fields.Char('License Plate')
    chassis_no1 = fields.Char('Chassis No')
    fuel_type1 = fields.Selection([('diesel', 'Diesel'),
                                   ('petrol', 'Petrol'),
                                   ('cng', 'CNG')], string='Fuel Type')
    service_details1 = fields.Text('Servise Details')
    service_nature1 = fields.Selection([('full_service', 'Full Service')], string='Nature of Services')
    under_guarantee1 = fields.Selection([('yes', 'Yes'),
                                         ('no', 'No')], string='Under Guarantee')
    gaurantee_type1 = fields.Selection([('paid', 'Paid'),
                                        ('free', 'Free')], string='Gaurantee Type')
    car_status1 = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'),
                                    ('done', 'Done')], default='draft')
    test1 = fields.Boolean(default=0)
    estm_serv_hr = fields.Float('Estimated Service Hours', digit=(4, 3))
    service_product = fields.Selection([('car_service', 'Car Service')], string='Service Product')
    service_product_price = fields.Float('Service Product Price', digit=(4, 3))
    product_line = fields.One2many('spare.product.line', 'spare_p')

    def enter_result(self):
        self.test1 = True
        self.car_status1 = 'in_progress'


class SparePart(models.Model):
    _name = 'spare.product.line'

    spare_p = fields.Many2one('fleet.info.line')
    spare_product = fields.Many2one('product.product', 'Product')
    spare_quantity = fields.Integer('Quantity')
    spare_unit_price = fields.Float('Unit Price', digit=(4, 2))

    @api.onchange('spare_product')
    def update_price(self):
        if self.spare_product:
            self.spare_unit_price=self.spare_product.lst_price

