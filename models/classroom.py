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
    
    validations_path = self.env['ir.config_parameter'].get_param('atenea.validations_path') or None
    if validations_path == None:
      _logger.error('La ruta de almacenamiento de convalidaciones no está definida')
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
      
    for submission in assignments[0].submissions():
      if len(submission.files) == 1:

        if not submission.files[0].is_zip:
          _logger.error('El archivo de convalidaciones debe ser un zip. Estudiante moodled id: {}'.format(submission.userid))
          return
        
        user = AteneaMoodleUser.from_userid(conn, submission.userid)
        
        grade = submission.load_grade()
        _logger.info("###############################")
        _logger.info(grade)
        path = '{}/{}/{}/'.format(validations_path, 
            '2223',  # TODO!! poner curso actual
            course_abbr) 
       
        path = path.replace('//', '/')

         # creación del directorio para descomprimirlo
        if not os.path.exists(path):  
          os.makedirs(path)
        
        # descarga del archivo
        filename = '[{}] - {}, {}'.format(
          user.id_,
          user.lastname.upper(), 
          user.firstname.upper())
          
        submission.files[0].from_url(conn = conn,url = submission.files[0].url)
        submission.files[0].save_as(path, filename + '.zip')

        # creación del directorio para descomprimirlo
        if not os.path.exists(path + filename):  
          os.makedirs(path + filename)

        submission.files[0].unpack_to(path + filename, remove_directories = False)
      else:
        _logger.error("Sólo está permitido subir un archivo. Estudiante moodle id: {}".format(submission.userid))

    return