from odoo import models, fields, api, _


class DeliveryTimeslotConfig(models.Model):
    _name = 'delivery.timeslot.config'

    def name_get(self):
        names = []
        for timeslot in self:
            name = str(timeslot.time_from)
            if timeslot.time_to:
                name += '-' + str(timeslot.time_to)
            names.append((timeslot.id, name))
        return names

    time_from = fields.Float(string="From")
    time_to = fields.Float(string="To")


class DeliveryTimeslotSetting(models.Model):
    _name = 'delivery.timeslot.setting'

    name = fields.Char(string="Name", default="Timeslot Setting")
    timeslot_ids = fields.Many2many('delivery.timeslot.config', 'display_timeslot_rel', 'disp_id', 'timeslot_id',
                                    string="Disable Time Slots")
    disable_timeslot_by_day_ids = fields.One2many('disable.timeslot.by.day', 'day_id', string="Disable Time Slots")
    disable_timeslot_by_date_ids = fields.One2many('disable.timeslot.by.date', 'dis_date_id', string="Disable Date Slots")


class DisableTimeSlotsByDay(models.Model):
    _name = 'disable.timeslot.by.day'

    d_day = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'),
                              ('5', 'Saturday'), ('6', 'Sunday')], string="Day")
    dis_timeslots_ids = fields.Many2many('delivery.timeslot.config', 'disable_display_timeslot_rel', 'day_id',
                                         'timeslot_id', string=" Disable Time Slots")
    day_id = fields.Many2one('delivery.timeslot.setting', string="Disable Time")


class DisableTimeSlotsByDate(models.Model):
    _name = 'disable.timeslot.by.date'

    disable_on_date = fields.Date(string="Disable Date")
    dis_timeslot_ids = fields.Many2many('delivery.timeslot.config', 'disable_display_timeslot_date_rel', 'date_id',
                                        'timeslot_id', string=" Disable Time Slots")
    dis_date_id = fields.Many2one('delivery.timeslot.setting', string="Disable Date")