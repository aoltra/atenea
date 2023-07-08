# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError

from odoo.exceptions import AccessDenied
from lxml import etree 

import datetime
import logging
import base64
import os

from ..support.helper import create_HTML_list_from_list
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
  
  student_id = fields.Many2one('atenea.student', string = 'Estudiante', required = True)
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

  # aporta información extra sobre el estado de la convalidación  
  situation = fields.Selection([
      ('0', ''),
      ('1', 'Pendiente de notificación al alumno'),
      ('2', 'Notificación enviada'),
      ('3', 'Nuevo envio de documentación'),
      ('4', 'Subsanación fuera de plazo'),
      ('5', 'Notificación rectificada (pendiente envio)'),
      ], string = 'Situación', default = '0',
      readonly = True)

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
      ], string ='Estado', help = 'Estado de la convalidación', 
      default = '0', compute = '_compute_state')
  
  # fecha de solicitud de la subsanación
  correction_date = fields.Date(string = 'Fecha subsanación', 
                                help = 'Fecha de publicación de la subsanación')
  
  correction_date_end = fields.Date(string = 'Fecha fin subsanación', 
                                    help = 'Fin de plazo de la subsanación',
                                    compute = '_compute_correction_date_end')

  # subsanación por razones de forma. Hace referencia a la entrega en si, no a 
  # cada uno de los módulos
  correction_reason = fields.Selection([
    ('MFL', 'Sólo se admite la entrega de un único fichero.'),
    ('NZP', 'La documentación aportada no se encuentra en un único fichero zip comprimido.'),
    ('NNX', 'No se encuentra un fichero llamado anexo o hay más de uno.'),
    ('ANC', 'Anexo no cumplimentado correctamente. Campos obligatorios no rellenados.'),
    ('ANP', 'Anexo no cumplimentado correctamente. Tipo (convalidación/aprobado con anterioridad) no indicado.'),
    ('SNF', 'Documento no firmado digitalmente'),
    ('INT', 'Ver convalidaciones módulos'), # subsanaciones específicas de módulos
    ('ERR1', 'Error al notificar una subsanación que no era'), 
    ('ERR2', 'Error al notificar los detalles de una subsanación'), 
    ], string ='Razón de la subsanación', 
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
  
  info = fields.Text(string = "Observaciones", compute = '_compute_info')

  def _default_locked(self):
    if (self.state == '2' and self.situation == '2') or self.situation == '5': 
      return True
    else:
      return False
    
  locked = fields.Boolean(default = _default_locked, store = False, readonly = True)
  
  _sql_constraints = [ 
    ('unique_validation', 'unique(school_year_id, student_id, course_id)', 
       'Sólo puede haber una convalidación por estudiante, ciclo y curso escolar.'),
  ]
  
  """ @api.onchange('validation_subjects_ids')
  def _check_notify_correction_done(self):
    self.ensure_one()
    if self.situation == '2' and self.state == '2':
      for val in self.validation_subjects_ids:
        old_val = next((old_vali for old_vali in self._origin.validation_subjects_ids if old_vali.id == val._origin.id), None)
        if old_val == None:
         return
        if not self.unlocked and \
           ((old_val.state == '1' and val.state != '1') or \
           (old_val.state != '1' and val.state == '1') or \
           (old_val.state == '1' and (old_val.correction_reason != val.correction_reason or old_val.comments != val.comments))):
            val.state = old_val.state
            val.correction_reason = old_val.correction_reason
            val.comments = old_val.comments
        elif self.unlocked and \
           ((old_val.state == '1' and val.state != '1') or \
           (old_val.state != '1' and val.state == '1') or \
           (old_val.state == '1' and (old_val.correction_reason != val.correction_reason or old_val.comments != val.comments))):
            return { 'warning': {
              'title': "¡Atención!", 
              'message': "Este cambio modifica el contenido de la notificación enviada al estudiante. Una vez guardada se le notificará de manera inmediata el cambio"
              }} """
  
  def write(self, vals):
    """
    Actualiza en la base de datos un registro
    """
    # impide que se realice más de una subsanación (INT)
    if self.situation == '3':
      if 'validation_subjects_ids' in vals and \
         'validation_subjects_for_correction_ids' in vals:
        
        # comprobación de que no haya ningún estado nuevo diferente de resulto o instancia superior
        for val in vals['validation_subjects_ids']:
          if val[2] != False and 'state' in val[2] and (val[2]['state'] =='0' or val[2]['state'] =='1'):
            raise ValidationError('Sólo se permite una subsanación. Todas las convalidaciones tienen, por tanto, que estar resueltas o enviadas a una instancia superior')
        
        # comprobación de que no quede ninguna en estado de subsanación. Si quedase al menos 1 
        # implicaria volver a realizar el proceso de subsanación y sólo se permite una vez
        for vfc in vals['validation_subjects_for_correction_ids']:
          val = next((vl for vl in vals['validation_subjects_ids'] if vl[1] == vfc[1]), None)
          if val[2] == False:
            raise ValidationError('Sólo se permite una subsanación. Todas las convalidaciones tienen, por tanto, que estar resueltas o enviadas a una instancia superior')

        
        vals['situation'] = '0'

    return super(Validation, self).write(vals)


  def create_correction(self, reason, comment = '') -> str:
    """
    Modifica la convalidación asignando los parámetros de subsanación
    Devuelve la notificación en formato HTML
    """
    if reason == None:
      raise Exception('Es necesario definir una razón para la subsanación')
    
    self.correction_date = datetime.datetime.today()
    
    footer = """
      <br>\
      <p>Se abre un periodo de subsanación de 15 días naturales a contar desde el día de publicación de este mensaje para reenviar \
        a través de esta misma tarea la documentación necesaria para corregir los errores. \
          Si pasado este periodo no se subsana el error, la(s) convalidación(es) afectadas se considerarán rechazadas.</p>
      <p>Recuerde enviar de nuevo TODA la documentación, incluso la ya entregada en envios previos</p>   
      <p><strong>Fin de período de subsanación</strong>: {0}</p>
      """.format(self.correction_date_end)

    # si la notificación previa es erronea
    prebody = ''
    if reason[:3] == 'ERR':
      prebody = """
          <p><strong>ATENCIÓN:</strong> La notificación previa fue enviada de manera errónea debido a un error administrativo. Esta notificación sustituye a la anterior. Disculpe las molestias</p>"""

    if reason == 'ERR1':
      body = prebody + '<p>Su convalidación se encuentra en estado: <strong>EN PROCESO</strong></p>.'

      self.write({ 
        'correction_reason': False,
        'state': '1',
        'correction_date': False
      })

      return body
    
    self.write({ 
      'correction_reason': reason,
      'state': '2',
      'correction_date': self.correction_date
    })
    
    # las causas viene definidas en cada uno de los módulos
    if reason in ('INT', 'ERR2'): 
      val_for_correction = [(dict(val._fields['correction_reason'].selection).get(val.correction_reason)) for val in self.validation_subjects_ids if val.state == '1']
      body = prebody + create_HTML_list_from_list(val_for_correction, 'No es posible realizar la convalidación solicitada por los siguientes motivos:')
    else:
      body = """
          <p>No es posible realizar la convalidación solicitada por los siguientes motivos:</p>
          <p style="padding-left: 1rem">(01) {0}</p>
          """.format(dict(self._fields['correction_reason'].selection).get(reason))

    feedback = body + comment + footer

    return feedback

  @api.depends('correction_date')
  def _compute_correction_date_end(self):
    for record in self:
      if record.correction_date == False:
        record.correction_date_end = False
      else:
        record.correction_date_end = record.correction_date + datetime.timedelta(days = 15)

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
     
  @api.depends('validation_subjects_not_for_correction_ids.is_read_only')
  def _compute_info(self):
    self.ensure_one()

    if int(self.state) == 2 and self.situation == '2':
      unlocked_info = ''
      if any(val.is_read_only == False for val in self.validation_subjects_ids):
        unlocked_info = '\n¡IMPORTANTE! Alguna convalidación ha sido desbloqueada para ser modificada. Si se modifica y se graba el estudiante será notificado de manera inmediata del nuevo estado de la convalidación'
      
      self.info = 'La convalidación está en estado de subsanación y ya ha sido notificada al estudiante.' + unlocked_info
      return
    
    self.info = f'La convalidación se encuentra en proceso de {dict(self._fields["state"].selection).get(self.state)} y no puede ser modificada'

    if (self.env.user.has_group('atenea.group_ROOT')) or \
       (self.env.user.has_group('atenea.group_ADMIN') and int(self.state) != 13) or \
       (self.env.user.has_group('atenea.group_MNGT_FP') and int(self.state) < 11) or \
       (self.env.user.has_group('atenea.group_VALID') and int(self.state) < 6):
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

  @api.depends('validation_subjects_ids')
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
      any_finished = any(val.state == '6' for val in record.validation_subjects_ids)
      all_finished = all(val.state == '6' for val in record.validation_subjects_ids)
      all_closed = all(val.state == '7' for val in record.validation_subjects_ids)

      # si está ya notificado al estudiante o estaba en subsanación o finalizada o instancia superior
      if record.situation == '2':
        # si hay alguna subsanación/instancia superior es que es subsanación/instancia superior
        if any_correction and any_higher_level:
          record.state = '4'
          continue
        
        # si hay alguna subsanación es que es subsanación
        if any_correction:
          record.state = '2'
          continue
      
        # si hay alguna instancia superior es que es instancia superior
        if any_higher_level:
          record.state = '3'
          continue

      # con notificación enviada se han realizado cambios
      if record.situation == '5':
        # alguno se ha pasado a no procesada (solo lo puede hacer admin)
        if any_noprocess:
          record.state = '1' # En proceso
          return

        # si hay instancias superiores y subsanaciones -> subsanación/instancia superior
        if any_higher_level and any_correction:
          record.state = '4'
          continue

        # si hay alguna en instancia superior -> instancia superior
        if any_higher_level:
          record.state = '3'
          continue
    
        # si hay al menos una subsanación  -> subsanacion
        if any_correction:
          record.state = '2'
          continue
      
        if all_resolved:
          record.state = '5' # Resuelta
          continue
      
      if record.situation == '3':
        record.state = '2'
        continue

      record.situation = '0'

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
      if all_finished:
        record.state = '13'
        continue

      if all_closed:
        record.state = '14'
        continue

      # si hay instancias superiores y subsanaciones -> subsanación/instancia superior
      if any_higher_level and any_correction:
        record.state = '4'
        record.situation = '1'
        continue

      # si hay alguna en instancia superior y no hay ninguna pendiente -> instancia superior
      if any_higher_level and not any_noprocess:
        record.state = '3'
        continue
      
      # si hay al menos una subsanación y no hay ninguna pendiente -> subsanacion
      if any_correction and not any_noprocess:
        record.state = '2'
        record.situation = '1'
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
      if any_finished and any_reviewed and any_higher_level:
        record.state = '10'
        continue

      # si sólo hay finalizadas e instancias superiores -> Finalizada parcialmente
      if any_finished and any_higher_level:
        record.state = '11'
        continue

      # si hay alguna sin finalizar y otras ya finalizadas -> en proceso de finalización
      if any_finished and any_reviewed:
        record.state = '12'
        continue
        
      if all_closed:
        record.state = '14'
        continue