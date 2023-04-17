# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import datetime
import logging
import os

_logger = logging.getLogger(__name__)

class Validation(models.Model):
  """
  Define la entrega de convalidaciones por parte del alumnado
  """
  _name = 'atenea.validation'
  _description = 'Convalidaciones'

  school_year_id = fields.Many2one('atenea.school_year', string = 'Curso escolar')
  
  student_id = fields.Many2one('atenea.student', string = 'Estudiante')
  student_name = fields.Char(related = 'student_id.name') 
  student_surname = fields.Char(related = 'student_id.surname') 
  student_nia = fields.Char(related = 'student_id.nia') 
  student_info = fields.Char(string = 'Estudiante', compute = '_compute_full_student_info')

  course_id = fields.Many2one('atenea.course', string = 'Ciclo', required = True)
  course_abbr = fields.Char(string = 'Ciclo', related = 'course_id.abbr')

  validation_subjects_ids = fields.One2many('atenea.validation_subject', 'validation_id', string = 'Módulos que se solicita convalidar')
  validation_subjects_info = fields.Char(string = 'Resueltas / Solicitadas', compute = '_compute_validation_subjects_info')
  
  # TODO que hacer con instancia superior si tardan en responder??
  # una opción es pasado un tiempo enviar el mail de confirmación al alumno
  # y finalizarla parcialmente
  state = fields.Selection([
      ('0', 'Sin procesar'),
      ('1', 'Subsanación'),
      ('2', 'Instancia superior'),
      ('3', 'Resuelta'),
      ('4', 'Revisada'),
      ('5', 'Finalizada'),
      ('6', 'Finalizada parcialmente'),
      ('7', 'En proceso'),
      ], string ='Estado de la convalidación', default = '0')
  
  # fecha de solicitud de la subsanación
  correction_date = fields.Date()

  correction_reason = fields.Selection([
    ('---', ''),   # no hay pendiente ninguna subsanación
    ('MFL', 'Sólo se admite la entrega de un único fichero.'),
    ('NZP', 'La documentación aportada no se encuentra en un único fichero zip comprimido.'),
    ('NNX', 'No se encuentra un fichero llamado anexo o hay más de uno.'),
    ('ANC', 'Anexo no cumplimentado correctamente. Campos obligatorios no rellenados.'),
    ('ANP', 'Anexo no cumplimentado correctamente. Tipo (convalidación/aprobado con anteriorirdad) no indicado.'),
    ('SNF', 'Documento no firmado digitalmente'),
    ('RL', 'No se aporta curso de riesgo laborales > 30h'),
    ('EXP', 'No se aporta expediente académico'),
    ], string ='Razón de la subsanación', default = '---',
    help = "Permite indicar el motivo por el que se solicita la subsanación")
  
  _sql_constraints = [ 
    ('unique_validation', 'unique(school_year_id, student_id, course_id)', 
       'Sólo puede haber una convalidación por estudiante, ciclo y curso escolar.'),
  ]

  def create_correction(self, reason):
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

    feedback = """
        <p>No es posible realizar la convalidación solicitada por los siguientes motivos:</p>
        <ul><li>{0}</ul>
        <p>Se abre un periodo de subsanación de 10 días a contar desde el día de publicación de este mensaje. Si pasado este periodo no se subsana el error, la(s) convalidación(es) afectadas se considerarán rechazadas.</p>
        <p><strong>Fin de período de subsanación</strong>: {1}</p>
        """.format(dict(self._fields['correction_reason'].selection).get(reason), self.correction_date + datetime.timedelta(days = 10))

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


  # TODO realizar un campo compute para actulizar el estado en función del estado de las convalidaciones de los modulos

