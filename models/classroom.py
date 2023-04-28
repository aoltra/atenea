# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta, datetime

from ..support.helper import is_set_flag, set_flag, get_data_from_pdf
from ..support import constants
from ..support.atenea_logger.exceptions import AteneaException

# Moodle
from ..support.atenea_moodleteacher.atenea_moodle_connection import AteneaMoodleConnection
from moodleteacher.connection import MoodleConnection      # NOQA
from ..support.atenea_moodleteacher.atenea_moodle_assignments import AteneaMoodleAssignments 
from ..support.atenea_moodleteacher.atenea_moodle_user import AteneaMoodleUser, AteneaMoodleUsers

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
  

  def _enrol_student(self, user, subject_id, course_id):
    """
    Matricula a un usuario atenea en un módulo
    Si no existe el usuario,  lo crea

    user: usuario moodle
    subject_id: identificador atenea del módulo
    course_id: identificador atenea del ciclo 
    """

    # comprobación: ya está en Atenea
    # devuelve un recorset
    student = self.env['atenea.student'].search([('moodle_id', '=', user.id_)])
    if len(student) == 0:
      # No existe, se crea el estudiante Atenea
      new_student = self.env['atenea.student'].create({
        'moodle_id': user.id_,
        'name': user.firstname,
        'surname': user.lastname,
        'email': user.email
      })
      _logger.info('Creando en Atenea al estudiante moodle_id:{}'.format(user.id_))
    else: 
      _logger.info('El estudiante moodle_id:{} ya existe en Atenea'.format(user.id_))
      new_student = student[0]

    enrolled = new_student.subjects_ids.filtered(lambda r: r.id == subject_id)

    if len(enrolled) == 0:
      # No está matriculado en ese módulo, se matricula
      # el 4 añade una relación entre el record y el record relacionado (subject_id)
      # Al menos en la versión 13, en relaciones M2M con tabla intermedia personalizada no crea el registro
      # así que se crea de manera manual
      self.env['atenea.subject_student_rel'].create({
        'student_id': new_student.id,
        'subject_id': subject_id,
        'course_id': course_id
      })

      # y luego se vincula
      new_student.subjects_ids = [ (4, subject_id, 0 )] 
      _logger.info("Estudiante moodle_id:{} no matriculado en el módulo_atenea_id: {} -> Matriculando".format(user.id_,course_id))
    else:
      _logger.info("Alumno moodle_id:{} ya estaba matriculado en el módulo_atenea_id: {}".format(user.id_, course_id))

    return new_student
    
  def _assigns_end_date_validation_period(self, conn, validation_classroom_id, subject_id, course_id, current_school_year):
    """
    Asignación de la fecha fin de plazo del periodo de convalidaciones
    Se actualiza la fecha de todos los participantes en caso de que aún no la
    tengan asignada.

    Devuelve un array de tuplas (moodle_user_id, nueva fecha)
    """

    users = AteneaMoodleUsers.from_course(conn, validation_classroom_id, only_students = True)

    users_to_change_due_date = []
    today = date.today()

    for user in users:
      a_user = self._enrol_student(user, subject_id, course_id)

      subject_student = self.env['atenea.subject_student_rel']\
        .search([('subject_id', '=', subject_id),('student_id', '=', a_user.id),('course_id', '=', course_id)])
      
      # aún no tiene abierto el periodo de convalidaciones
      if not is_set_flag(subject_student[0].status_flags,constants.VALIDATION_PERIOD_OPEN):
        # asigno un periodo de 30 dias de plazo
        if current_school_year.date_init_lective > today: # el proceso ha ocurrido antes de abrir las aulas virtuales
          new_due_date = current_school_year.date_init_lective + timedelta(days = 31)
        else:
          new_due_date = today + timedelta(days = 31)
          
        users_to_change_due_date.append((user.id_,int(datetime(year = new_due_date.year, 
                     month = new_due_date.month,
                     day = new_due_date.day).timestamp())))
        
        # indicamos que ese usuario ya tiene el periodo abierto
        subject_student[0].write({
          'status_flags': set_flag(subject_student.status_flags,constants.VALIDATION_PERIOD_OPEN)
        })
     
    return users_to_change_due_date

  @api.model
  def cron_download_validations(self, validation_classroom_id, subject_id, validation_task_id, course_id):
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
    
    current_sy = (self.env['atenea.school_year'].search([('state', '=', 1)])) # curso escolar actual  

    if len(current_sy) == 0:
      raise AteneaException(
          _logger, 
          'No se ha definido un curso actual',
          50, # critical
          comments = '''Es posible que no se haya marcado como actual ningún curso escolar''')
    else:
      current_school_year = current_sy[0]
        

    # obtención de las tareas entregadas
    assignments = AteneaMoodleAssignments(conn, 
      course_filter=[validation_classroom_id], 
      assignment_filter=[validation_task_id])
    
    if len(assignments) == 0:
      raise AteneaException(
          _logger, 
          'No se ha encontrado la tarea para convalidaciones (moodle_id: {})'.format(validation_task_id),
          50, # critical
          comments = '''Es posible que la tarea con moodle_id:{} no exista en moodle o no
                      exista dentro del curso con moodle_id: {}. 
                      Es posible que se haya creado un nuevo curso escolar y no se haya
                      actualizado los moodle_id dentro de atenea'''.
                      format(validation_task_id, validation_classroom_id))
    
    assignments[0].set_extension_due_date(self._assigns_end_date_validation_period(
        conn, 
        validation_classroom_id, 
        subject_id, 
        course_id,
        current_school_year))
  
    # creación del directorio del ciclo para descomprimir las convalidaciones
    today = date.today()
    course = self.env['atenea.course'].browse([course_id])
    path = '{}/{}/{}/'.format(validations_path, 
          '%s_%s' % (current_school_year.date_init.year, current_school_year.date_init.year + 1),  # TODO!! poner curso actual
          course.abbr) 
       
    path = path.replace('//', '/')

    if not os.path.exists(path):  
      os.makedirs(path)

    # comprobación de cada una de las tareas
    for submission in assignments[0].submissions():
      
      user = AteneaMoodleUser.from_userid(conn, submission.userid)   # usuario moodle
      a_user =  self._enrol_student(user, subject_id, course_id)  # usuario atenea
  
      # obtención de la convalidación 
      validation_list = [ val for val in a_user.validations_ids if val.course_id.id == course_id]
      
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
      # en caso de subsanación se abre un perido de 15 dias naturales
      new_due_date = today + timedelta(days = 15)
      new_timestamp =  int(datetime(year = new_due_date.year, 
                         month = new_due_date.month,
                         day = new_due_date.day).timestamp())
      
      if len(submission.files) == 0:
        continue

      # más de un fichero enviado (debería ser comprobado en Moodle)
      if len(submission.files) != 1:
        _logger.error("Sólo está permitido subir un archivo. Estudiante moodle id: {} {}".format(submission.userid, len(submission.files)))      
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('MFL'))
        submission.set_extension_due_date(to = new_timestamp)
        continue

      # fichero no en formato zip  (debería ser comprobado en Moodle)
      if not submission.files[0].is_zip:
        _logger.error('El archivo de convalidaciones debe ser un zip. Estudiante moodle id: {}'.format(submission.userid))
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('NZP')) 
        submission.set_extension_due_date(to = new_timestamp)
        continue
 
      # descarga del archivo
      filename = '[{}] {}, {}'.format(
        user.id_,
        user.lastname.upper() if user.lastname is not None else 'SIN-APELLIDOS', 
        user.firstname.upper() if user.firstname is not None else 'SIN-NOMBRE')
  
      submission.files[0].from_url(conn = conn,url = submission.files[0].url)
      submission.files[0].save_as(path, filename + '.zip')
   
      # creación del directorio para descomprimirlo
      if not os.path.exists(path + filename):  
        os.makedirs(path + filename)

      submission.files[0].unpack_to(path + filename, remove_directories = False)

      for file in os.listdir(path + filename):
        os.rename(os.path.join(path + filename, file), os.path.join(path + filename, file.upper()))

      files_unzip = []
      for file in os.listdir(path + filename):
        if os.path.isfile(os.path.join(path + filename, file)):
            files_unzip.append(file.upper())

      annex_file = [file for file in files_unzip if 'ANEXO' in file or 'ANNEX' in file]

      # más de un anexo (o ninguno)
      if len(annex_file) != 1:
        _logger.error("Es necesario que haya un (y sólo un) fichero llamado anexo. Estudiante moodle id: {} {}".format(submission.userid, len(annex_file)))   
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('NNX'))
        submission.set_extension_due_date(to = new_timestamp)
        continue
  
      # datos obligatorios rellenados  
      fields = get_data_from_pdf(path + filename +'/' + annex_file[0])
      _logger.info(fields)

      missing_fields = []
      for mandatory_field in constants.PDF_VALIDATION_FIELDS_MANDATORY:
        assert isinstance(mandatory_field, tuple),  f'Valor incorrecto en constants.PDF_VALIDATION_FIELDS_MANDATORY. Cada entrada tiene que ser una tupla'
        assert isinstance(mandatory_field[0], (str, tuple)), f'Valor incorrecto en constants.PDF_VALIDATION_FIELDS_MANDATORY. La primera entrada de cada tupla o es una str o una tuple'
        
        if isinstance(mandatory_field[0], str):
          assert mandatory_field[0] in fields, f'La clave {mandatory_field[0]} no existe en el pdf'

          # un campo obligatorio no está definido
          if fields[mandatory_field[0]][constants.PDF_FIELD_VALUE] is None or \
             len(fields[mandatory_field[0]][constants.PDF_FIELD_VALUE]) == 0:
              missing_fields.append(mandatory_field[1])

        elif isinstance(mandatory_field[0], tuple):
          exist = False
          for option in mandatory_field[0]:
            if (fields[option][constants.PDF_FIELD_TYPE] != 'Button' and \
                fields[option][constants.PDF_FIELD_VALUE] is not None and \
                len(fields[option][constants.PDF_FIELD_VALUE]) != 0) or \
               (fields[option][constants.PDF_FIELD_TYPE] == 'Button' and fields[option][constants.PDF_FIELD_VALUE] == 'Yes'):
              exist = True

          if not exist:
            missing_fields.append(mandatory_field[1])

      if len(missing_fields) > 0:
        _logger.error("Faltan campos obligatorios por definir en el pdf. Estudiante moodle id: {} {}".format(submission.userid, missing_fields))
        # TODO, descomentar. Se comenta para facilitar las pruebas
        #submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('ANC'))
        #submission.set_extension_due_date(to = new_timestamp)
        continue

      # integridad en la selección de campos
      paired_fields = []
      for paired_field in constants.PDF_VALIDATION_FIELDS_PAIRED:
        assert isinstance(paired_field, tuple),  f'Valor incorrecto en constants.PDF_VALIDATION_FIELDS_PAIRED. Cada entrada tiene que ser una tupla'

        if  ((fields[paired_field[0]][constants.PDF_FIELD_TYPE] != 'Button' and \
            fields[paired_field[0]][constants.PDF_FIELD_VALUE] is not None and \
            len(fields[paired_field[0]][constants.PDF_FIELD_VALUE]) != 0) or \
            (fields[paired_field[0]][constants.PDF_FIELD_TYPE] == 'Button' and fields[paired_field[0]][constants.PDF_FIELD_VALUE] == 'Yes')) and \
            ((fields[paired_field[1]][constants.PDF_FIELD_TYPE] != 'Button' and \
            fields[paired_field[1]][constants.PDF_FIELD_VALUE] is None or \
            len(fields[paired_field[1]][constants.PDF_FIELD_VALUE]) == 0) or \
            (fields[paired_field[1]][constants.PDF_FIELD_TYPE] == 'Button' and fields[paired_field[0]][constants.PDF_FIELD_VALUE] == 'Off')):
              paired_fields.append(paired_field[1])

      #if len(paired_field) > 0:
      #  _logger.error("No se han definido correctamente si se solicita AA o CO. Estudiante moodle id: {} {}".format(submission.userid, paired_fields))
        # TODO, descomentar. Se comenta para facilitar las pruebas
        #submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('ANP'))
        #submission.set_extension_due_date(to = new_timestamp)
        continue

      # TODO comprobación de firma digital

      # asignacion de módulos a CO/AA
      validation_subjects = []
      
      # TODO comprobar y eliminar si es el caso, si un mismo módulo aparece más de una vez
      for key in fields:
        _logger.info("asdasasd1" + key)

        # es el nombre del módulo
        if key.startswith('C_Modulo') and len(key) < 12:
          code = fields[key][0][:4]
          
          if len(code) == 0:
            continue
          
          subject = self.env['atenea.subject'].search([('code', '=', code)])
            
          if len(subject) == 0:
            raise AteneaException(
              _logger, 
              'No se encuentra en Atenea el módulo con código {}'.format(code),
              50, # critical
              comments = '''Tal vez falten módulos por codificar o que el código del PDF no sea el correcto. Código: {}
                '''. format(code))
          _logger.info("asdasasd3")
          valid_subject = (0, 0, {
            'subject_id': subject.id,
            'state': '0',
            'validation_type': 'aa'  # TODO: ajustarlo según el PDF
          }) 
      
          validation_subjects.append(valid_subject)

      # añade nuevos registro, pero los mantiene en "el aire" hasta que se grabe el school_year 
      validation.validation_subjects_ids = validation_subjects

      """ 
        
      grade = submission.load_grade()
      _logger.info("###############################")
      _logger.info(grade)
    
        
      """
  
 
    return
  
  
  @api.model
  def cron_enrol_students(self, validation_classroom_id, course_id, subject_id):
    """
    Asocia (matricula) estudiantes en un aula

    validation_classroom_id: aula de Moodle de la que tiene que coger los usuarios
    subject_id: identificador de Atenea de la materia en la que se matricula
    course_id: identificador del ciclo formativo

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
      self._enrol_student(user, subject_id, course_id)