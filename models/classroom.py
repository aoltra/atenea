# -*- coding: utf-8 -*-

from odoo import models, fields, api

from ..support.atenea_moodle_connection import AteneaMoodleConnection
from moodleteacher.assignments import MoodleAssignments    # NOQA  

import logging

_logger = logging.getLogger(__name__)

class Classroom(models.Model):
  """
  Define un aula virtual
  """

  _name = 'atenea.classroom'
  _description = 'Aula virtual'

  moodle_id = fields.Integer('Identificador Moodle', required = True)
  code = fields.Char('Código', required = True, help = 'Código del aula, por ejemplo SEG9_CEE_46025799_2022_854101_0498')
  description = fields.Char('Descripción')

  subjects_ids = fields.One2many('atenea.subject', 'classroom_id', string = 'Módulos')
  tasks_moodle_ids = fields.One2many('atenea.task_moodle', 'classroom_id', string = 'Tareas que están conectadas con Atenea')

  """ Devuelve la tarea encargada de las convalidaciones """
  def get_task_id_by_key(self, key):
    
    tasks = list(filter(lambda item: item['key'] == key, self.tasks_moodle_ids))
    if not tasks:
      _logger.error("No hay tarea de convalidaciones en el aula")
      return None

    return tasks[0].moodle_id

  @api.model
  def _cron_download_validations(self, validation_classroom_id, validation_task_id):
    if validation_classroom_id == None:
      _logger.error("CRON: validation_classroom_id no definido")
      return
    
    if validation_task_id == None:
      _logger.error("CRON: validation_task_id no definido")
      return

    _logger.info("CRRROOON id {}".format(validation_task_id))
    
    conn = AteneaMoodleConnection( 
      moodle_user = self.env['ir.config_parameter'].get_param('atenea.moodle_user'), 
      moodle_host = self.env['ir.config_parameter'].get_param('atenea.moodle_url'))

 


    return