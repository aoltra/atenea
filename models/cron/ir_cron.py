# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# https://github.com/OCA/server-tools/blob/8.0/cron_inactivity_period/models/ir_cron.py

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

""" Clase hija de cron que añade diferentes periodos de inactividad"""
class IrCron(models.Model):
  _inherit = 'ir.cron'

  inactivity_period_ids = fields.One2many('ir.cron.inactivity.period', 
    string = 'Periodos de inactividad',
    inverse_name = 'cron_id')

  @api.model
  def _callback(self, model_name, method_name, args, job_id):
    job = self.browse(job_id)
    # se comprueba si es periodo de inactividad, 
    # es decir, si _check_inactivity_period devuelve True
    if any(job.inactivity_period_ids._check_inactivity_period()):
        _logger.info(
          "Job %s skipped during inactivity period",
           job.name)
        return
    
    return super(IrCron, self)._callback(
      model_name, method_name, args, job_id)
