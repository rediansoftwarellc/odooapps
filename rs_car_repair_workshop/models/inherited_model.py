from odoo import models, fields, api, _


class WorkOr(models.Model):
    _inherit = 'sale.order'

    car_repair_origin = fields.Char('Repair Origin')
    work_count = fields.Char('Work Count', compute='compute_work_order')
    repair_order_count = fields.Char('Repair Order', compute='compute_repair_order')

    def action_confirm(self):
        res = super(WorkOr, self).action_confirm()
        sas = self.env['car.repair'].search([('ref', '=', self.car_repair_origin)])
        aas = self.env['car.diagnosis'].search([('repair_ref', '=', self.car_repair_origin)])
        for rec in sas:
            ras = rec.car_info_line
            for dec in ras:
                for pec in aas:
                    das = pec.fleet_info_line
                    for hec in das:
                        for lec in hec.product_line:
                            dict = {'work_order': sas.subject,
                                    'client_w': self.partner_id.id,
                                    'no_of_hr': hec.estm_serv_hr,
                                    'repair_origin1': sas.ref,
                                    'priority_w': sas.priority,
                                    'assigned_to1': pec.technician.id,
                                    'work_line': [(0, 0, {
                                        'car3': dec.car.id,
                                        'model3': dec.model.id,
                                        'chassis_no3': dec.chassis_no,
                                        'license_plate3': dec.license_plate,
                                        'fuel_type3': dec.fuel_type,
                                        'under_guarantee3': dec.under_guarantee,
                                        'service_nature3': dec.service_nature,
                                        'diagnosis_result_line': [
                                            (0, 0, {'spare_product1': lec.spare_product.id,
                                                    'spare_quantity1':lec.spare_quantity})]
                                    })],
                                    }
                            print('11111111111',dict)
                            self.env['work.order'].create(dict)
                        # print('222222',dict)
                        # self.env['work.order'].create(dict)
            #         print('3333',dict)
            #     print('444444444',dict)
            #
            # print('55555555',dict)
                            #self.env['work.order'].create(dict)
        self.env['car.repair'].search([('ref', '=', self.car_repair_origin)]).update(
            {'repair_status': 'approve quatation'})

        return res


    def compute_work_order(self):
        self.work_count = self.env['work.order'].search_count([('repair_origin1', '=', self.car_repair_origin)])


    def compute_repair_order(self):
        self.repair_order_count = self.env['car.repair'].search_count([('ref', '=', self.car_repair_origin)])


    def get_work_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Work Order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'work.order',
            'domain': [('repair_origin1', '=', self.car_repair_origin)]
        }


    def get_repair_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repair Order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'car.repair',
            'domain': [('ref', '=', self.car_repair_origin)]}


class Qut(models.Model):
    _inherit = 'sale.order.line'

    license_plate = fields.Char('License Plate')
    model = fields.Many2one('fleet.vehicle.model', 'Model')
