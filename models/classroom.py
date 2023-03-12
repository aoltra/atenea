# -*- coding: utf-8 -*-

from odoo import models, fields, api

from ..support.atenea_moodle_connection import AteneaMoodleConnection
from moodleteacher.connection import MoodleConnection      # NOQA
from moodleteacher.assignments import MoodleAssignments    # NOQA  
from ..support.atenea_moodle_user import AteneaMoodleUser 

import os
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

  _sql_constraints = [ 
    ('unique_moodle_id', 'unique(moodle_id)', 'El identificador de moodle tiene que ser único.'),
  ]

  """ Devuelve la tarea encargada de las convalidaciones """
  def get_task_id_by_key(self, key):
    
    tasks = list(filter(lambda item: item['key'] == key, self.tasks_moodle_ids))
    if not tasks:
      _logger.error("No hay tarea de convalidaciones en el aula")
      return None

    return tasks[0].moodle_id

  @api.model
  def _cron_download_validations(self, validation_classroom_id, validation_task_id, course_abbr):
    if validation_classroom_id == None:
      _logger.error("CRON: validation_classroom_id no definido")
      return
    
    if validation_task_id == None:
      _logger.error("CRON: validation_task_id no definido")
      return
    
    if course_abbr == None:
      _logger.error("CRON: course_abbr no definido")
      return

    # _logger.info("CRRROOON id {}".format(validation_task_id))
    
    try:
      conn = AteneaMoodleConnection( 
        moodle_user = self.env['ir.config_parameter'].get_param('atenea.moodle_user'), 
        moodle_host = self.env['ir.config_parameter'].get_param('atenea.moodle_url')) 
    except Exception:
      raise Exception('No es posible realizar la conexión con Moodle')
  
    _logger.info("CRRROOON id {}".format(conn))

    assignments = MoodleAssignments(conn, 
      course_filter=[validation_classroom_id], 
      assignment_filter=[validation_task_id])
      

    #users = AteneaMoodleUser.get_data_users_from_id(conn, [12055, 12048])
    # users = MoodleUser.from_userid(conn, 2)

    #for a in assignments:
    for submission in assignments[0].submissions():
      if len(submission.files) == 1:
        user = AteneaMoodleUser.from_userid(conn, submission.userid)
        
        grade = submission.load_grade()
        _logger.info("###############################")
        _logger.info(grade)
        if not os.path.exists('/mnt/atenea_data/convalidaciones/{}/{} - {}, {}'
          .format(course_abbr, user.id_, user.lastname.upper(), user.firstname.upper())):
          _logger.info("#########################NOOOO######")
          os.makedirs('/mnt/atenea_data/convalidaciones/{}/{} - {}, {}'
          .format(course_abbr, user.id_, user.lastname.upper(), user.firstname.upper()))
      

    return