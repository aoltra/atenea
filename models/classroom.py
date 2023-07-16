# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta, datetime

from ..support.helper import is_set_flag, set_flag, get_data_from_pdf, create_HTML_list_from_list
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
  _rec_name = 'code'

  moodle_id = fields.Integer('Identificador Moodle', required = True)
  code = fields.Char('Código', required = True, help = 'Código del aula, por ejemplo SEG9_CEE_46025799_2022_854101_0498')
  description = fields.Char('Descripción')

  subjects_ids = fields.One2many('atenea.subject', 'classroom_id', string = 'Módulos')
  tasks_moodle_ids = fields.One2many('atenea.task_moodle', 'classroom_id', string = 'Tareas que están conectadas con Atenea')

  lang_id = fields.Many2one('res.lang', domain = [('active','=', True)])

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
  
    path = os.path.join(validations_path, 
          '%s_%s' % (current_school_year.date_init.year, current_school_year.date_init.year + 1), 
          course.abbr) 

    if not os.path.exists(path):  
      os.makedirs(path)

    # comprobación de cada una de las tareas
    # TODO: probar con un parámetro en submission must_have_files = True
    for submission in assignments[0].submissions():
      # esta comprobación se hace la primera para evitar problemas de resto de datos que puede
      # haber en el tarea de Moodle
      if len(submission.files) == 0:
        _logger.info("No hay ficheros en la entrega")
        continue

      new_documentation = False

      _logger.info("Entrega usuario moodle {}".format(submission.userid))   
      user = AteneaMoodleUser.from_userid(conn, submission.userid)   # usuario moodle
      a_user =  self._enrol_student(user, subject_id, course_id)  # usuario atenea
  
      # obtención de la convalidación 
      validation_list = [ val for val in a_user.validations_ids if val.course_id.id == course_id]
      
      if len(validation_list) == 0:
        validation = self.env['atenea.validation'].create([
            { 'student_id': a_user.id,
              'course_id': course_id,
              'attempt_number': submission.attemptnumber + 1,
              'school_year_id': current_school_year.id }])
      else:
        validation = validation_list[0]

        _logger.info("Intento de entrega A{}:M{}".format(validation.attempt_number, submission.attemptnumber + 1))   

        if validation.attempt_number == submission.attemptnumber + 1: # no ha habido cambios en la entrega
          continue
        else:
          # esta condición está pensanda para el caso en el que hay una nueva entrega, pero también controla
          # el caso de que sean diferentes por problemas de sincronización entre Moodle y Atenea:
          # si el registro desaparece de atenea => se iguala al de Moodle (en la creación de la convalidación)
          # si el registro desaparece en Moodle => Atenea se igual al de Moodle
          validation.attempt_number = submission.attemptnumber + 1
          new_documentation = True
 
      ############                     ############
      ##### comprobación de errores a subsanar ####
      ############                     ############
      # en caso de subsanación se abre un perido de 15 dias naturales
      new_due_date = today + timedelta(days = 15)
      new_timestamp =  int(datetime(year = new_due_date.year, 
                         month = new_due_date.month,
                         day = new_due_date.day,
                         hour = 23,
                         minute = 59,
                         second = 59).timestamp())     
      
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
      foldername = '[{}] {}, {}'.format(
        user.id_,
        user.lastname.upper() if user.lastname is not None else 'SIN-APELLIDOS', 
        user.firstname.upper() if user.firstname is not None else 'SIN-NOMBRE')
      
      filename = '[{}][{}] {}, {}'.format(
        user.id_,
        submission.attemptnumber + 1,
        user.lastname.upper() if user.lastname is not None else 'SIN-APELLIDOS', 
        user.firstname.upper() if user.firstname is not None else 'SIN-NOMBRE')

      # creación del directorio para almacenarlo
      path_user = os.path.join(path, foldername, '') 
      if not os.path.exists(path_user):  
        os.makedirs(path_user)

      submission.files[0].from_url(conn = conn, url = submission.files[0].url)
      submission.files[0].save_as(path_user, filename + '.zip')
      
      # creación del directorio para descomprimirlo
      path_user_submission = os.path.join(path_user, filename, '') 
      if not os.path.exists(path_user_submission):
        os.makedirs(path_user_submission)

      # lo descomprime. si el fichero existe, lo sobreescribe
      submission.files[0].unpack_to(path_user_submission, remove_directories = False)

      files_unzip = []
      for file in os.listdir(path_user_submission):
        os.rename(os.path.join(path_user_submission, file), os.path.join(path_user_submission, file.upper()))

      for file in os.listdir(path_user_submission):
        if os.path.isfile(os.path.join(path_user_submission, file)):
            files_unzip.append(file)
  
      _logger.info(files_unzip)
        
      annex_file = [file for file in files_unzip if 'ANEXO' in file or 'ANNEX' in file]

      # más de un anexo (o ninguno)
      if len(annex_file) != 1:
        _logger.error("Es necesario que haya un (y sólo un) fichero llamado anexo o annex. Estudiante moodle id: {} {}".format(submission.userid, len(annex_file)))   
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('NNX'))
        submission.set_extension_due_date(to = new_timestamp)
        continue
  
      # datos obligatorios rellenados  
      fields = get_data_from_pdf(os.path.join(path_user_submission, annex_file[0]))
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
              break

          if not exist:
            missing_fields.append(mandatory_field[1])

      if len(missing_fields) > 0:
        _logger.error('Faltan campos obligatorios por definir en el pdf. Estudiante moodle id: {} {}'.format(submission.userid, missing_fields))
        submission.save_grade(3, new_attempt = True, 
                                 feedback = validation.create_correction('ANC', 
                                                                         create_HTML_list_from_list(missing_fields, 'Campos a revisar:')))
        submission.set_extension_due_date(to = new_timestamp)
        continue

      # integridad en la selección de campos
      paired_fields = []
      for paired_field in constants.PDF_VALIDATION_FIELDS_PAIRED:
        assert isinstance(paired_field, tuple),  f'Valor incorrecto en constants.PDF_VALIDATION_FIELDS_PAIRED. Cada entrada tiene que ser una tupla'

        if  ((fields[paired_field[0]][constants.PDF_FIELD_TYPE] != 'Button' and \
            fields[paired_field[0]][constants.PDF_FIELD_VALUE] is not None and \
            len(fields[paired_field[0]][constants.PDF_FIELD_VALUE]) != 0) or \
            (fields[paired_field[0]][constants.PDF_FIELD_TYPE] == 'Button' and \
            fields[paired_field[0]][constants.PDF_FIELD_VALUE] == 'Yes')) and \
            ((fields[paired_field[1]][constants.PDF_FIELD_TYPE] != 'Button' and \
            fields[paired_field[1]][constants.PDF_FIELD_VALUE] is None or \
            len(fields[paired_field[1]][constants.PDF_FIELD_VALUE]) == 0) or \
            (fields[paired_field[1]][constants.PDF_FIELD_TYPE] == 'Button' and \
             fields[paired_field[0]][constants.PDF_FIELD_VALUE] == 'Off')):
              paired_fields.append(fields[paired_field[0]][constants.PDF_FIELD_VALUE])

      if len(paired_fields) > 0:
        _logger.error("No se han definido correctamente si se solicita AA o CO. Estudiante moodle id: {} {}".format(submission.userid, paired_fields))
        # TODO, descomentar. Se comenta para facilitar las pruebas
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('ANP'))
        submission.set_extension_due_date(to = new_timestamp)
        continue

      # TODO comprobación de firma digital

      # obtengo el NIA del formulario
      # aunque el login del alumno es su NIA, a dia de hoy Aules no me lo proporciona
      a_user.write({
        'nia': fields['A_NIA'][0]
      })

      # asignacion de módulos a CO/AA
      validation_subjects = []
      validation_subjects_code_previous = {}
      # diccionario con todos los code de los modulos solicitados en la anterior entrega
      for val_subject in self.env['atenea.validation_subject'].search([('validation_id', '=', validation.id)]):
        validation_subjects_code_previous[val_subject.subject_id.code] = {
          'id': val_subject.subject_id.id,
          'type': val_subject.validation_type } 

      # TODO comprobar y eliminar si es el caso, si un mismo módulo aparece más de una vez
      id_subjects = []
      for key in fields:

        # es el nombre del módulo
        if key.startswith('C_Modulo') and len(key) < 12:
          code = fields[key][0][:(fields[key][0].find(' -'))]
          validation_type = fields[key + 'AACO'][0][:2].lower()
          
          if len(code) == 0:
            continue

          if code in validation_subjects_code_previous and \
              validation_subjects_code_previous[code]['type'] == validation_type:
              del validation_subjects_code_previous[code]
              continue
          
          subject = self.env['atenea.subject'].search([('code', '=', code)])
            
          if len(subject) == 0:
            raise AteneaException(
              _logger, 
              'No se encuentra en Atenea el módulo con código {}'.format(code),
              50, # critical
              comments = '''Tal vez falten módulos por codificar o que el código del PDF no sea el correcto. Código: {}
                '''. format(code))

          if code not in validation_subjects_code_previous:
            valid_subject = (0, 0, {
              'subject_id': subject.id,
              'state': '0',
              'validation_type': validation_type 
            }) 
          else:
            # actualizo el registro con el nuevo tipo de validación
            valid_subject = (1, validation_subjects_code_previous[code]['id'], {
              'validation_type': validation_type 
            }) 
            del validation_subjects_code_previous[code]
    
          # lo añade a la lista si no existe ya => en caso de módulo repetido
          # se queda con la primera aparición
          if subject.id not in id_subjects: 
            validation_subjects.append(valid_subject)
            id_subjects.append(subject.id)

      # los módulos solicitados en anteriores entregas que no han sido solcitados en esta
      # se eliminan
      for val_key in validation_subjects_code_previous:
        _logger.error(" va: {} {}".format(validation_subjects_code_previous[val_key], validation.id))
        self.env['atenea.validation_subject']. \
          search([('subject_id', '=', validation_subjects_code_previous[val_key]['id']),
                  ('validation_id', '=', validation.id)]). \
                  unlink()

      # añade nuevos registro, pero los mantiene en "el aire" hasta que se grabe el school_year 
      validation.validation_subjects_ids = validation_subjects
      # ha pasado los filtros iniciales => cambio el estado a en proceso
      submission.save_grade(2)
  
      if new_documentation:
        validation.situation = '3'

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

  @api.model
  def cron_notify_validations(self, validation_classroom_id, validation_task_id, course_id, correction_notification =  False):
    """
    Publica notificaciones sobre las convalidaciones 
    correction notification indica si es una notificación para realizar una corrección sobre una notificación anterior
    """
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
    
    if not correction_notification:
      validations = self.env['atenea.validation'].search([('course_id', '=', course_id)])
    else:
      validations = self.env['atenea.validation'].search([('course_id', '=', course_id), ('situation','=', '5')])

    if len(validations) == 0:
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
    
    today = date.today()

    # en caso de subsanación se abre un perido de 15 dias naturales
    new_due_date = today + timedelta(days = 15)
    new_timestamp = int(datetime(year = new_due_date.year, 
                      month = new_due_date.month,
                      day = new_due_date.day,
                      hour = 0,
                      minute = 1,
                      second = 0).timestamp())     
    
    submissions = assignments[0].submissions()
    
    for validation in validations:

      # obtengo la primera entrega que tenga como estudiante al que se indica en la convalidación
      submission = next((sub for sub in submissions if sub.userid == int(validation.student_id.moodle_id)), None)
      if submission == None:
        _logger.error(f'No es posible encontrar en la tarea de Moodle {validation_task_id} la entrega del usuario id A{submission.user_id}:A{validation.student_id}')
        continue

      # está en estado de subsanación y el alumno no ha sido avisado
      if validation.state == '2' and validation.situation == '1':
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('INT'))
        submission.set_extension_due_date(to = new_timestamp)
        # TODO comprobar que la nota se haya almacenado correctamente en Moodle
        validation.write({
          'situation': '2'  
        })

      # está en estado de proceso, instancia superior o resuelto y el alumno había sido notificado de una subsanación
      if validation.state in ('1','3','5') and validation.situation == '5':
        submission.save_grade(2, new_attempt = False, feedback = validation.create_correction('ERR1'))
        # submission.set_extension_due_date(to = new_timestamp)
        # TODO comprobar que la nota se haya almacenado correctamente en Moodle
        validation.write({
          'situation': '0'  
        })

      # está en estado de subsanación o subsanacion/instancia superior y el alumno había sido notificado de una subsanación
      if validation.state in('2','4') and validation.situation == '5':
        submission.save_grade(3, new_attempt = True, feedback = validation.create_correction('ERR2'))
        submission.set_extension_due_date(to = new_timestamp)
        # TODO comprobar que la nota se haya almacenado correctamente en Moodle
        validation.write({
          'situation': '2'  
        })

      # está finalizada
      if validation.state == '13':
        submission.save_grade(4, new_attempt = False, feedback = validation.create_finished_notification_message())


  @api.model
  def cron_check_deadline_validations(self, course_id):
    today = date.today()
    validations = self.env['atenea.validation'].search([('course_id', '=', course_id)])

    for val in validations:
      if today > val.correction_date_end:
        val.write({
          'situation': '4'  
        })