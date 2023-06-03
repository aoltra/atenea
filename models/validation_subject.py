# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging
import os

_logger = logging.getLogger(__name__)

class ValidationSubject(models.Model):
  """
  Define los módulos a convalidar
  """
  _name = 'atenea.validation_subject'
  _description = 'Módulo a convalidar'

  validation_id = fields.Many2one('atenea.validation', string = 'Convalidación', required = True)
  subject_id = fields.Many2one('atenea.subject', string = 'Módulo', required = True)
  teacher_id = fields.Many2one('atenea.employee', string = 'Resuelta por')
  
  validation_type = fields.Selection([
      ('aa', 'Aprobado con Anterioridad'),
      ('co', 'Convalidación'),
      ], string ='Tipo de convalidación', default = 'aa',
      help = "Permite indicar si la convalidación es un aprobado con anterioridad (mismo código de módulo) o una convalidación")
  
  mark = fields.Selection([
      ('5', '5'),
      ('6', '6'),
      ('7', '7'),
      ('8', '8'),
      ('9', '9'),
      ('10', '10'),
      ('11', 'MH')
      ], string =" Nota")
  
  comments = fields.Text(string = 'Comentarios',
                         help = 'Ciclo aportado, centro donde se cursó, titulación de inglés aportada...')
  # accepted = fields.Boolean(default = False)
  accepted = fields.Selection([
      ('1', 'Sí'),
      ('2', 'No')
      ], string = "Aceptada")
  
  state = fields.Selection(selection = '_populate_state', 
                           string ='Estado de la convalidación', default = '0')
  
  validation_reason = fields.Selection([
      ('FOLRL', 'Ciclo LOGSE + RL (>30h)'),
      ('B2', 'Título B2'),
      ('AA', 'Común con otro ciclo formativo'),
      ], string ='Razón de la convalidación', 
      help = "Permite indicar el motivo por el que acepta o deniega la convalidación")
  
  correction_reason = fields.Selection([
    ('ANC', 'Anexo no cumplimentado correctamente. Campos obligatorios no rellenados.'),
    ('ANP', 'Anexo no cumplimentado correctamente. Tipo (convalidación/aprobado con anterioridad) no indicado.'),
    ('SNF', 'Documento no firmado digitalmente'),
    ('RL', 'No se aporta curso de riesgo laborales > 30h'),
    ('EXP', 'No se aporta expediente académico'),
    ], string ='Razón de la subsanación',
    help = "Permite indicar el motivo por el que se solicita la subsanación")
  
  """  # la nota tiene que estar entre 5 (tiene que esta aprobado) y 11
  @api.constrains('mark')
  def _check_mark(self):
    for record in self:
      if record.mark > 11 or record.mark < 5:
        raise ValidationError('El valor debe estar ente 5 y 11') """
      
  """ 
    # contrains via sql
    _sql_constraints = [
    ('mark', 'check(mark > 4 and mark < 12)', 'El valor debe estar ente 5 y 11'),
  ] """

  def _populate_state(self):
    """
    Rellena el selection en función del grupo al que pertenece el usuario
    """
    choices = [('0', 'Sin procesar'),
               ('1', 'Subsanación'),
               ('2', 'Instancia superior'),
               ('3', 'Resuelta'),    
               ('4', 'Revisada'),
               ('5', 'Por revisar'), # desde secretaria ven un error y la tiran para atrás
               ('6', 'Finalizada')]
    
    # if ordenados por orden de grupos de más importante a menos
    if self.env.user.has_group('atenea.group_ROOT'): # root todas las opciones
      return choices
    
    if self.env.user.has_group('atenea.group_MNGT_FP'): # coordinación de FP todas menos finalizar y por revisar
      del choices[-2:]
    elif self.env.user.has_group('atenea.group_VALID'): # convalidadores, todas menos las tres últimas
      del choices[-3:]
    elif self.env.user.has_group('atenea.group_ADMIN'): # Secretaria sólo las tres últimas
      del choices[:-3]
    else: # cualquier otro grupo no tiene opciones
      choices.clear()

    return choices 
  
  def _check_attribute_value(self, field_name, vals) -> bool:
    if isinstance(self._fields[field_name], fields.Char):
      return ((field_name in vals and vals[field_name] == '') or \
              (field_name not in vals and self[field_name] == ''))
    
    if isinstance(self._fields[field_name], fields.Selection):
      return ((field_name in vals and vals[field_name] == False) or \
              (field_name not in vals and self[field_name] == False))
    
    return False
 
  def write(self, vals):
    """
    Actualiza en la base de datos un registro
    """
    if 'state' in vals: # si cambia el estado
      # si el estado es subsanación tiene que haber una razón
      if vals['state'] == '1' and self._check_attribute_value('correction_reason', vals): 
        raise ValidationError(f'La convalidación de {self.subject_id.name} tiene un estado de subsanación y no se ha definido la razón')

      # si el estado es instancia superior tiene que haber un comentario  
      if vals['state'] == '2' and self._check_attribute_value('comment', vals): 
        raise ValidationError(f'La convalidación de {self.subject_id.name} se ha escalado a un instancia superior y no se ha definido un comentario justificándolo')
      
      if int(vals['state']) > 2 and \
        (self._check_attribute_value('mark', vals) or \
         self._check_attribute_value('validation_reason', vals) or \
         self._check_attribute_value('validation_type', vals) or \
         self._check_attribute_value('accepted', vals) or \
         self._check_attribute_value('comment', vals)):
          raise ValidationError(f'La convalidación de {self.subject_id.name} no ha definido la nota y/o la razón y/o un comentario')
      
      # si no es subsanación se elimina la razon
      if vals['state'] != '1':
        vals['correction_reason'] = False

    else:  
      # si el estado es subsanación tiene que haber una razón
      if self.state == '1' and self._check_attribute_value('correction_reason', vals): 
        raise ValidationError(f'La convalidación de {self.subject_id.name} tiene un estado de subsanación y no se ha definido la razón')
      
      # si el estado es instancia superior tiene que haber un comentario  
      if self.state == '2' and self._check_attribute_value('comment', vals): 
        raise ValidationError(f'La convalidación de {self.subject_id.name} se ha escalado a un instancia superior y no se ha definido un comentario justificándolo')
   
      if int(self.state) > 2 and \
        (self._check_attribute_value('mark', vals) or \
         self._check_attribute_value('validation_reason', vals) or \
         self._check_attribute_value('validation_type', vals) or \
         self._check_attribute_value('accepted', vals) or \
         self._check_attribute_value('comment', vals)):
          raise ValidationError(f'La convalidación de {self.subject_id.name} no ha definido la nota y/o la razón y/o un comentario')

    return super(ValidationSubject, self).write(vals)
  
  def _create_validations(self):
    validations_path = self.env['res.config_parameter'].sudo().get_param('validation_path') or None
    if validations_path == None:
        self._logger.error('El directorio de convalidaciones no está definido')
        return
    
    courses = self.env['atenea.course'].search([])

    # bucle por cada ciclo
    for course in courses:
      validations_path_course = validations_path + '/' + course.abbr
      files = []

      for file_path in os.listdir(validations_path_course):
        if os.path.isfile(os.path.join(validations_path_course, file_path)):
          files.append(file_path) # aunque mejor hacer ya la descompresion, no?
