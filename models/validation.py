# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import datetime
import logging
import base64
import os

from ..support.atenea_logger.exceptions import AteneaException

_logger = logging.getLogger(__name__)

class Validation(models.Model):
  """
  Define la entrega de convalidaciones por parte del alumnado
  """
  _name = 'atenea.validation'
  _description = 'Solicitud convalidación'
  _rec_name = 'student_info' 

  school_year_id = fields.Many2one('atenea.school_year', string = 'Curso escolar')
  
  student_id = fields.Many2one('atenea.student', string = 'Estudiante')
  student_name = fields.Char(related = 'student_id.name') 
  student_surname = fields.Char(related = 'student_id.surname') 
  student_nia = fields.Char(related = 'student_id.nia') 
  student_info = fields.Char(string = 'Estudiante', compute = '_compute_full_student_info')

  course_id = fields.Many2one('atenea.course', string = 'Ciclo', required = True)
  course_abbr = fields.Char(string = 'Ciclo', related = 'course_id.abbr')

  validation_subjects_ids = fields.One2many('atenea.validation_subject', 'validation_id', 
     string = 'Módulos que se solicita convalidar')

  validation_subjects_not_for_correction_ids = fields.One2many('atenea.validation_subject', 
  'validation_id', 
    string = 'Módulos que se solicita convalidar', 
    domain = [('state', '!=', '1')],
    compute = '_compute_validation_subjects_not', readonly = False)

  validation_subjects_for_correction_ids = fields.One2many('atenea.validation_subject', 'validation_id', 
    string = 'Módulos pendientes de subsanación',
    domain = [('state', '=', '1')],
    compute = '_compute_validation_subjects', readonly = False)
     
  validation_subjects_info = fields.Char(string = 'Resueltas / Solicitadas', compute = '_compute_validation_subjects_info')
  
  # TODO que hacer con instancia superior si tardan en responder??
  # una opción es pasado un tiempo enviar el mail de confirmación al alumno
  # y finalizarla parcialmente
  state = fields.Selection([
      ('0', 'Sin procesar'),
      ('1', 'En proceso'),
      ('2', 'Subsanación'),
      ('3', 'Instancia superior'),
      ('4', 'Subsan. / Inst. superior'),
      ('5', 'Resuelta'),
      ('6', 'En proceso de revisión'),
      ('7', 'En proceso de revisión (parcial)'), # algunas revisadas, otras aun resueltas y algunas elevadas a una instancia superior
      ('8', 'Revisada'),
      ('9', 'Revisada parcialmente'),
      ('10', 'En proceso de finalización (parcial)'),
      ('11', 'Finalizada parcialmente'),
      ('12', 'En proceso de finalización'),
      ('13', 'Finalizada'), # todas las convalidaciones finalizadas pero sin notificación al alumno
      ('14', 'Cerrada'),
      ], string ='Estado de la convalidación', default = '0',
      compute = '_compute_state')
  
  # fecha de solicitud de la subsanación
  correction_date = fields.Date()

  correction_reason = fields.Selection([
    ('---', ''),   # no hay pendiente ninguna subsanación
    ('MFL', 'Sólo se admite la entrega de un único fichero.'),
    ('NZP', 'La documentación aportada no se encuentra en un único fichero zip comprimido.'),
    ('NNX', 'No se encuentra un fichero llamado anexo o hay más de uno.'),
    ('ANC', 'Anexo no cumplimentado correctamente. Campos obligatorios no rellenados.'),
    ('ANP', 'Anexo no cumplimentado correctamente. Tipo (convalidación/aprobado con anterioridad) no indicado.'),
    ('SNF', 'Documento no firmado digitalmente'),
    ('RL', 'No se aporta curso de riesgo laborales > 30h'),
    ('EXP', 'No se aporta expediente académico'),
    ], string ='Razón de la subsanación', default = '---',
    help = 'Permite indicar el motivo por el que se solicita la subsanación')
  
  # numeración basada en 1: 1,2,3,4...
  attempt_number = fields.Integer(string = 'Número de entregas realizadas', default = 1,
                                  readonly = True, 
                                  help = 'Indica el número actual de veces que ha realizado la subida de la documentación debido a subsanaciones')

  documentation = fields.Binary(string = "Documentación")
  documentation_filename = fields.Char(
        string='Nombre del fichero',
        compute='_compute_documentation_filename'
    )
  
  info = fields.Char(string="Información", compute = '_compute_info')
  
  _sql_constraints = [ 
    ('unique_validation', 'unique(school_year_id, student_id, course_id)', 
       'Sólo puede haber una convalidación por estudiante, ciclo y curso escolar.'),
  ]

  def create_correction(self, reason, comment = ''):
    """
    Modifica la convalidación asignando los parámetros de subsanación
    """
    if reason == None:
      raise Exception('Es necesario definir una razón para la subsanación')
    
    self.correction_date = datetime.datetime.today()
    
    self.write({ 
      'correction_reason': reason,
      'state': '1',
      'correction_date': self.correction_date
    })

    footer = """
      <br>\
      <p>Se abre un periodo de subsanación de 15 días naturales a contar desde el día de publicación de este mensaje. \
         Si pasado este periodo no se subsana el error, la(s) convalidación(es) afectadas se considerarán rechazadas.</p>
      <p><strong>Fin de período de subsanación</strong>: {0}</p>
      """.format(self.correction_date + datetime.timedelta(days = 15))

    body = """
        <p>No es posible realizar la convalidación solicitada por los siguientes motivos:</p>
        <p style="padding-left: 1rem">(01) {0}</p>
        """.format(dict(self._fields['correction_reason'].selection).get(reason))

    feedback = body + comment + footer

    return feedback

  def _compute_full_student_info(self):
    for record in self:
      if record.student_nia == False:
        record.student_info = record.student_surname + ', ' + record.student_name
      else: 
        record.student_info = '(' + record.student_nia + ') ' + record.student_surname + ', ' + record.student_name

  def _compute_validation_subjects_info(self):
    for record in self:
        num_resolved = len([val for val in record.validation_subjects_ids if val.state == '3'])
        record.validation_subjects_info = f'{num_resolved} / {len(record.validation_subjects_ids)}'

  @api.depends('validation_subjects_not_for_correction_ids')
  def _compute_validation_subjects(self):
    #for validation in self:
      self.ensure_one()
      self.validation_subjects_for_correction_ids = self.validation_subjects_ids.filtered(lambda t: t.state == '1')
      self.validation_subjects_not_for_correction_ids = self.validation_subjects_ids.filtered(lambda t: t.state != '1')

  @api.depends('validation_subjects_for_correction_ids')
  def _compute_validation_subjects_not(self):
    self.ensure_one()
    self.validation_subjects_for_correction_ids = self.validation_subjects_ids.filtered(lambda t: t.state == '1')
    self.validation_subjects_not_for_correction_ids = self.validation_subjects_ids.filtered(lambda t: t.state != '1')

  def _compute_documentation_filename(self):
    self.ensure_one()
    self.documentation_filename = '[{}][{}] {}, {}'.format(
        self.student_id.moodle_id,
        self.attempt_number,
        self.student_surname.upper() if self.student_surname is not None else 'SIN-APELLIDOS', 
        self.student_name.upper() if self.student_name is not None else 'SIN-NOMBRE')
     
  def _compute_info(self):
    self.ensure_one()

    self.info = f'La convalidación se encuentra en proceso de {dict(self._fields["state"].selection).get(self.state)} y no puede ser modificada'

    if (self.env.user.has_group('atenea.group_ROOT')) or \
       (self.env.user.has_group('atenea.group_ADMIN') and int(self.state) != 13) or \
       (self.env.user.has_group('atenea.group_MNGT_FP') and int(self.state) < 11) or \
       (self.env.user.has_group('atenea.group_VALID') and int(self.state) < 5):
      self.info =''  
  
  
  def download_validation_action(self):
    """
    Descarga la última versión de la documentación
    """
    self.ensure_one() # esta función sólo puede ser llamada por un único registro, no por un recordset

    # el acceso a ir.config_parameter sólo es posible desde el administrador. 
    # para que un usuario no admin (por ejemplo un convalidador) pueda acceder a descargar la documuentación
    # se utiliza la función sudo() para saltar los reglas de acceso
    validations_path = self.env['ir.config_parameter'].sudo().get_param('atenea.validations_path') or None
    if validations_path == None:
      _logger.error('La ruta de almacenamiento de convalidaciones no está definida')
      return

    current_sy = (self.env['atenea.school_year'].search([('state', '=', 1)])) # curso escolar actual  

    if len(current_sy) == 0:
      raise AteneaException(
          _logger, 
          'No se ha definido un curso actual',
          50, # critical
          comments = '''Es posible que no se haya marcado como actual ningún curso escolar''')
    else:
      current_school_year = current_sy[0]

    path = os.path.join(validations_path, 
          '%s_%s' % (current_school_year.date_init.year, current_school_year.date_init.year + 1), 
          self.course_abbr) 

    foldername = '[{}] {}, {}'.format(
        self.student_id.moodle_id,
        self.student_surname.upper() if self.student_surname is not None else 'SIN-APELLIDOS', 
        self.student_name.upper() if self.student_name is not None else 'SIN-NOMBRE')
      
    filename = '[{}][{}] {}, {}'.format(
        self.student_id.moodle_id,
        self.attempt_number,
        self.student_surname.upper() if self.student_surname is not None else 'SIN-APELLIDOS', 
        self.student_name.upper() if self.student_name is not None else 'SIN-NOMBRE')

    documentation_filename = f'{path}/{foldername}/{filename}.zip'
    with open(documentation_filename, 'rb') as f:
      file_bytes = f.read()
      encode_data = base64.b64encode(file_bytes)

    self.documentation = encode_data

    return {
      'type': 'ir.actions.act_url',
      'url': 'web/content?model=atenea.validation&id=%s&field=documentation&filename=%s.zip&download=true' % 
        (self.id, filename.replace(' ','%20'))
    }

  def _compute_state(self):
    for record in self:
      all_noprocess = all(val.state == '0' for val in record.validation_subjects_ids)
      any_noprocess = any(val.state == '0' for val in record.validation_subjects_ids)
      any_correction = any(val.state == '1' for val in record.validation_subjects_ids)
      any_higher_level = any(val.state == '2' for val in record.validation_subjects_ids)
      any_resolved = any(val.state == '3' for val in record.validation_subjects_ids)
      all_resolved = all(val.state == '3' for val in record.validation_subjects_ids)
      all_reviewed = all(val.state == '4' for val in record.validation_subjects_ids)
      any_reviewed = any(val.state == '4' for val in record.validation_subjects_ids)
      any_ended = any(val.state == '6' for val in record.validation_subjects_ids)
      all_ended = all(val.state == '6' for val in record.validation_subjects_ids)
      all_closed = all(val.state == '7' for val in record.validation_subjects_ids)

      # si todas sin procesar -> sin procesar
      if all_noprocess:
        record.state = '0'
        continue

      # si todas resueltas -> resuelta
      if all_resolved:
        record.state = '5'
        continue
  
      # si todas revisada -> revisada
      if all_reviewed:
        record.state = '8'
        continue
      
      # si todas finalizadas -> finalizada
      if all_ended:
        record.state = '13'
        continue

      if all_closed:
        record.state = '14'
        continue

      # si hay instancias superiores y subsanaciones -> subsanación/instancia superior
      if any_higher_level and any_correction:
        record.state = '4'
        continue

      # si hay alguna en instancia superior y no hay ninguna pendiente -> instancia superior
      if any_higher_level and not any_noprocess:
        record.state = '3'
        continue
      
      # si hay al menos una subsanación y no hay ninguna pendiente -> subsanacion
      if any_correction and not any_noprocess:
        record.state = '2'
        continue

      # si hay alguna sin procesar y otras ya resueltas o pendientes de subsanación o a instancias superiores -> en proceso
      if any_noprocess and (any_resolved or any_correction or any_higher_level):
        record.state = '1'
        continue

      # si hay alguna sin revisar y otras ya revisadas -> en proceso de revision (parcial)
      if any_resolved and any_reviewed and any_higher_level:
        record.state = '7'
        continue

      # si sólo hay revisadas y instancias superiores -> Revisada parcialmente
      if any_reviewed and any_higher_level:
        record.state = '9'
        continue

      # si hay alguna sin revisar y otras ya revisadas -> en proceso de revision
      if any_resolved and any_reviewed:
        record.state = '6'
        continue

      # si hay alguna sin finalizar y otras ya finalizadas -> en proceso de finalización (parcial)
      if any_ended and any_reviewed and any_higher_level:
        record.state = '10'
        continue

      # si sólo hay finalizadas e instancias superiores -> Finalizada parcialmente
      if any_ended and any_higher_level:
        record.state = '11'
        continue

      # si hay alguna sin finalizar y otras ya finalizadas -> en proceso de finalización
      if any_ended and any_reviewed:
        record.state = '12'
        continue
        
      if all_closed:
        record.state = '14'
        continue