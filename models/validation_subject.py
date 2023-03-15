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
  mark = fields.Integer(string = "Nota")
  comments = fields.Char()
  accepted = fields.Boolean(default = False)
  state = fields.Selection([
      ('0', 'Sin procesar'),
      ('1', 'Subsanación'),
      ('2', 'Instancia superior'),
      ('3', 'Resuelta'),
      ('4', 'Revisada'),
      ('5', 'Finalizada'),
      ], string ='Estado de la convalidación', default = '0')
  

  validation_reason = fields.Selection([
      ('FOLRL', 'Ciclo LOGSE + RL (>30h)'),
      ('B2', 'Título B2'),
      ('AA', 'Común con otro ciclo formativo'),
      ], string ='Razón de la convalidación', 
      help = "Permite indicar el motivo por el que acepta o deniega la convalidación")


  # la nota tiene que estar entre 5 (tiene que esta aprobado) y 11
  @api.constrains('mark')
  def _check_mark(self):
    for record in self:
      if record.mark > 11 or record.mark < 5:
        raise ValidationError('El valor debe estar ente 5 y 11')
      
  """ 
    # contrains via sql
    _sql_constraints = [
    ('mark', 'check(mark > 4 and mark < 12)', 'El valor debe estar ente 5 y 11'),
  ] """

  
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
