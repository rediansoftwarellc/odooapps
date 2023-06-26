from odoo import models,fields,api

class UpdateTechnician(models.TransientModel):
    _name="assign.technician"

    technician1=fields.Many2one('res.users','Technician')
    def technician_update(self):

        self.env['car.diagnosis'].browse(self._context.get('active_ids')).update(
            {'technician': self.technician1})
        self.env['car.diagnosis'].browse(self._context.get('active_ids')).update(
            {'diagnosis_status':'in_progress'})
