# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

from ..support.atenea_moodle_connection import AteneaMoodleConnection
from moodleteacher.connection import MoodleConnection      # NOQA
#from moodleteacher.assignments import MoodleAssignments    # NOQA  
from ..support.atenea_moodle_assignments import AteneaMoodleAssignments 
from ..support.atenea_moodle_user import AteneaMoodleUser, AteneaMoodleUsers

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
  def _cron_download_validations(self, validation_classroom_id, validation_task_id, course_id):

    # comprobaciones iniciales
    if validation_classroom_id == None:
      _logger.error("CRON: validation_classroom_id no definido")
      return
    
    if validation_task_id == None:
      _logger.error("CRON: validation_task_id no definido")
      return
    
    if course_id == None:
      _logger.error("CRON: course no definido")
      return
    
    validations_path = self.env['ir.config_parameter'].get_param('atenea.validations_path') or None
    if validations_path == None:
      _logger.error('La ruta de almacenamiento de convalidaciones no está definida')
      return
    
    try:
      conn = AteneaMoodleConnection( 
        moodle_user = self.env['ir.config_parameter'].get_param('atenea.moodle_user'), 
        moodle_host = self.env['ir.config_parameter'].get_param('atenea.moodle_url')) 
    except Exception:
      raise Exception('No es posible realizar la conexión con Moodle')
  
    # obtención de las tareas entregadas
    assignments = AteneaMoodleAssignments(conn, 
      course_filter=[validation_classroom_id], 
      assignment_filter=[validation_task_id])
      
    # comprobación de cada una de las tareaws
    for submission in assignments[0].submissions():
      
      user = AteneaMoodleUser.from_userid(conn, submission.userid)   # usuario moodle
      a_user_list = self.env['atenea.student'].search([('moodle_id', '=', submission.userid)]) # usuario atenea

      if len(a_user_list) == 0:
        a_user = self.env['atenea.student'].create([
            { 'moodle_id': submission.userid,
              'name': user.firstname,
              'surname': user.lastname,
              'email': user.email }])
      else:
        a_user = a_user_list[0]

      # obtención de la convalidación 
      validation_list = [ val for val in a_user.validations_ids if val.course_id.id == course_id]
      current_school_year = (self.env['atenea.school_year'].search([('state', '=', 1)]))[0] # curso escolar actual
      if len(validation_list) == 0:
        validation = self.env['atenea.validation'].create([
            { 'student_id': a_user.id,
              'course_id': course_id,
              'school_year_id': current_school_year.id }])
      else:
        validation = validation_list[0]

      ############                     ############
      ##### comprobación de errores a subsanar ####
      ############                     ############
      # más de un fichero enviado (debería ser comprobado en Moodle)
      if len(submission.files) != 1:
        _logger.error("Sólo está permitido subir un archivo. Estudiante moodle id: {}".format(submission.userid))      
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('MFL'))
        return

      # fichero no en formato zip  (debería ser comprobado en Moodle)
      if not submission.files[0].is_zip:
        _logger.error('El archivo de convalidaciones debe ser un zip. Estudiante moodle id: {}'.format(submission.userid))
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('NZP')) 
        return
      
      """ course = self.env['atenea.course'].browse([course_id])
        
      grade = submission.load_grade()
      _logger.info("###############################")
      _logger.info(grade)
      path = '{}/{}/{}/'.format(validations_path, 
          '%s/%s' % (current_school_year.date_init.year, current_school_year.date_init.year + 1),  # TODO!! poner curso actual
          course.abbr) 
       
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

      submission.files[0].unpack_to(path + filename, remove_directories = False) """
  
 
    return
  
  @api.model
  def cron_enrol_students(self, validation_classroom_id):
    """
    Asocia (matricula) estudiantes en un aula

    En caso de que el estudiante no se encuentre en Atenea lo crea
    """
    # comprobaciones iniciales
    if validation_classroom_id == None:
      _logger.error("CRON: validation_classroom_id no definido")
      return
    
    try:
      conn = AteneaMoodleConnection( 
        moodle_user = self.env['ir.config_parameter'].get_param('atenea.moodle_user'), 
        moodle_host = self.env['ir.config_parameter'].get_param('atenea.moodle_url')) 
    except Exception:
      raise Exception('No es posible realizar la conexión con Moodle')
  
    # obtención de los usuarios
    users = AteneaMoodleUsers.from_course(conn, validation_classroom_id, only_students = True)

    for user in users:
      # comprobacion: ya está en Atenea
      # devuelve un recorset
      student = self.env['atenea.student'].search([('moodle_id', '=', user.id_)])
      if len(student) == 0:
        _logger.info("el estudiante {} no existe".format(user.id_))
        # se crea el estudiante Atenea
      else: 
        _logger.info("el estudiante si existe")