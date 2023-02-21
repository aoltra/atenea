# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# https://raw.githubusercontent.com/OCA/server-tools/8.0/cron_inactivity_period/models/ir_cron_inactivity_period.py
# modificado por Alfredo Oltra

from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IrCronInactivityPeriod(models.Model):
  _name = 'ir.cron.inactivity.period'

  _SELECTION_TYPE = [
    ('hour', 'Hora'),
    ('day', 'Día'),
  ]

  cron_id = fields.Many2one('ir.cron', ondelete = 'cascade', required = True)

  type = fields.Selection(
    string = 'Type', selection = _SELECTION_TYPE,
    required = True, default = 'hour')

  inactivity_hour_begin = fields.Float(string = 'Horas de incio', default = 0)
  inactivity_hour_end = fields.Float(string = 'Hora de fin', default = 1)
  inactivity_day_begin = fields.Date(string = 'Día de inicio', default = date.today())
  inactivity_day_end = fields.Date(string = 'Día de fin', default = date.today())

  @api.constrains('inactivity_hour_begin', 'inactivity_hour_end')
  def _check_activity_hour(self):
    for period in self:
      if period.type != 'hour':
        continue
      if period.inactivity_hour_begin >= period.inactivity_hour_end:
        raise ValidationError(_(
          "La hora final debe ser mayor que la inicial"))
          
  @api.constrains('inactivity_day_begin', 'inactivity_day_end')
  def _check_activity_day(self):
    for period in self:
      if period.type != 'day':
        continue
      if period.inactivity_day_begin >= period.inactivity_day_end:
        raise ValidationError(_(
          "El día final debe ser mayor que el inicial"))

  def _check_inactivity_period(self):
    res = []
    for period in self:
      res.append(period._check_inactivity_period_one())
    return res

  def _check_inactivity_period_one(self):
    self.ensure_one()   # la función sólo puede procesar un registro
    now = fields.Datetime.context_timestamp(self, datetime.now())
    if self.type == 'hour':
      begin_inactivity = now.replace(
        hour = int(self.inactivity_hour_begin),
        minute = int((self.inactivity_hour_begin % 1) * 60),
        second = 0)
      end_inactivity = now.replace(
        hour = int(self.inactivity_hour_end),
        minute = int((self.inactivity_hour_end % 1) * 60),
        second = 0)
      return now >= begin_inactivity and now < end_inactivity
    elif self.type == 'day':
      return now.date() >= self.inactivity_day_begin and now.date() < self.inactivity_day_end
    else:
      raise ValidationError(
        _("Unimplemented Feature: Inactivity Period type '%s'") % (self.type))
