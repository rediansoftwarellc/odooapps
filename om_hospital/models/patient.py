from datetime import date
from odoo import api, fields, models
from dateutil import relativedelta


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Patient"

    name = fields.Char(string='Name', required=True)
    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string="Age", compute='_compute_age',inverse='_inverse_compute_age', tracking=True)
    note = fields.Text(string='Description')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'),('others', 'Others')], string='Gender', tracking=True)
    active = fields.Boolean(string='Active', default=True)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointments')
    image = fields.Image(string="Image")
    ref = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                      default=lambda self: ('New'))
    tag_ids = fields.Many2many('patient.tag', string="Tags")
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count', tracking=True)
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointments")

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        appointment_group = self.env['hospital.appointment'].read_group(domain=[('state', '=', 'done')], fields=['patient_id'], groupby=['patient_id'])

        for appointment in appointment_group:
            patient_id = appointment.get('patient_id')[0]
            patient_rec = self.browse(patient_id)
            patient_rec.appointment_count = appointment['patient_id_count']
            self -= patient_rec
        self.appointment_count = 0

    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.dob:
                rec.age = today.year - rec.dob.year
            else:
                rec.age = 1

    def _inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.dob = today - relativedelta.relativedelta(years=rec.age)

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Patient'
        if vals.get('reference', ('New')) == ('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient') or ('New')
        res = super(HospitalPatient, self).create(vals)
        return res

