# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# https://github.com/OCA/server-tools/blob/8.0/cron_inactivity_period/models/ir_cron.py

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

""" Clase hija de cron que añade enlaces many2one a:
    1. school_year. Tareas que afecten a toda la FP. Por ejemplo para convalidaciones o renuncias
    2. departament. Tareas que afecten a un departamento: mensajes de bienvenida, explicación de procedimientos, etc
    3. course (tutoria). Tareas que afecten a un ciclo: mensaje de bienvenida, convocatoria de reuniones, apertura o fin de plazos
    4. subject. Tareas que afecten a módulo: mensaje de bienvenida, mensajes de encuestas de examenes, mensajes de apertura de temas, etc
    5. employee. Tareas a nivel de empleado (experimental)
     
    4 y 5 se separan a efectos de usabilidad por parte del usuario, para separarlas conceptualmente en las diferentes partes de 
    la aplicación, pero en el fondo es lo mismo
    """
class IrCron(models.Model):
  _inherit = 'ir.cron'

  # Objectoid al que va asociado el cron, 
  # no confundir con el modelo que tiene el código a ejecutar.
  school_year_id = fields.Many2one('atenea.school_year', string = 'Curso escolar', ondelete = 'cascade')
 
  """ inactivity_period_ids = fields.One2many('ir.cron.inactivity.period', 
    string = 'Periodos de inactividad',
    inverse_name = 'cron_id') """
     
  def method_direct_trigger(self):
    self.check_access_rights('write')
    for cron in self:
      try:
        cron.with_user(cron.user_id).with_context({'lastcall': cron.lastcall}).ir_actions_server_id.run()
        cron.lastcall = fields.Datetime.now()
      except Exception:
        _logger.error('Se ha producido una excepción el cron_id: {}, name: {}'.format( 
          cron.id,
          cron.name))
    
    return True 
  

  """ @api.model
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
        model_name, method_name, args, job_id) """
    
