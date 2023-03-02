# -*- coding: utf-8 -*-

from odoo import models, fields, api

from moodleteacher.connection import MoodleConnection  

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
  tasks_moodle_ids = fields.One2many('atenea.task_moodle', 'classroom_id', string = 'Tareas que estám conectadas con Atenea')

  @api.model
  def _cron_example(self):
    _logger.info("CRON ATENEA-CEED")

    return
  
  @api.model
  def _cron_download_validations(self, validation_task_id):
    if validation_task_id == None:
      _logger.info("CRON: validation_task_id no definido")

    _logger.info("CRRROOON id {}".format(validation_task_id))

    
    conn = MoodleConnection(interactive=True, 
      token = "ad342bca211c70e18c6b28ae6b35c26", 
      moodle_host = "https://aules.edu.gva.es/ed/")


    _logger.info("CRRROOON con {}".format(conn))
    return