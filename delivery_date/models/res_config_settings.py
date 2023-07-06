from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    disable_date = fields.Boolean(string="Do You want to disable customer order delivery date pro feature", default=False)
    disable_comment = fields.Boolean(string="Do you want to disable customer order delivery comment feature", default=False)

    def set_values(self):
        config = self.env['ir.config_parameter']
        config.set_param("cust.disable_date", self.disable_date or False)
        config.set_param("cust.disable_comment", self.disable_comment or False)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            disable_date=get_param('cust.disable_date'),
            disable_comment=get_param('cust.disable_comment')
        )
        return res