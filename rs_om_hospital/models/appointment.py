from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Appointment"
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('hospital.patient', string="Patient", required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", related="patient_id.gender")
    appointment_time = fields.Datetime(string='Appointment Time', tracking=True)
    email = fields.Char(string='Email')
    booking_date = fields.Date(string='Booking Date', default=fields.Date.context_today, readonly='1')
    tag_ids = fields.Many2many('patient.tag', string="Tags", related="patient_id.tag_ids")
    ref = fields.Char(string='Reference', readonly='1', tracking=True)
    prescription = fields.Html(string='Prescription')
    state = fields.Selection([('draft', 'Draft'), ('in_consultation', 'In Consultation'),
                              ('done', 'Done'), ('cancel', 'Cancel')], default='draft', string='Status', required=True)
    doctor_id = fields.Many2one('res.users', string='Doctor')
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string='Pharmacy Lines')
    _order = 'booking_date desc'

    def patient_action(self):
        for val in self:
            return {
                'name': _('Patient'),
                'view_mode': 'form',
                'view_id': self.env.ref('om_hospital.view_patient_form').id,
                'res_model': 'hospital.patient',
                'type': 'ir.actions.act_window',
                'res_id': val.patient_id.id,
                'target': 'self',
            }


    #
    # @api.model
    # def create(self, vals):
    #     if not vals.get('doctor_id'):
    #         raise ValidationError("Please fill in the Doctor field.")
    #     return super(HospitalAppointment, self).create(vals)

    # def send_appointment_email(self):
    #     template = self.env.ref(
    #         'om_hospital.email_template_appointment')  # Replace with your actual template reference
    #     for appointment in self:
    #         template.with_context(
    #             default_model='hospital.appointment',
    #             default_res_id=appointment.id,
    #             default_use_template=bool(template),
    #             default_template_id=template and template.id or False,
    #             default_composition_mode='comment',
    #         ).send_mail(appointment.id, force_send=True)

    def send_appointment_email(self):
        self.ensure_one()
        template_id = self.env.ref('om_hospital.email_template_appointment')
        template_id.send_mail(self.id, force_send=True)

        # Rest of the class definition
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_test(self):
        print('Button Clicked')
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Click Successful',
                'type': 'rainbow_man',
            }
        }

    def in_consultation(self):
        for rec in self:
            rec.state = "in_consultation"

    def mark_as_done(self):
        for rec in self:
            rec.state = "done"

    def cancelled(self):
        for rec in self:
            rec.state = "cancel"

    def action_in_consultation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = "in_consultation"

    def action_done_p(self):
        for rec in self:
            if rec.state == 'in_consultation':
                rec.state = 'done'

    def action_cancel_o(self):
        for rec in self:
            if rec.state == 'in_consultation':
                rec.state = 'cancel'


class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    product_id = fields.Many2one('product.product')
    price_unit = fields.Float(related='product_id.list_price', required=True)
    qty = fields.Integer(string="Quantity", default=1)
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")


