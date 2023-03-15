# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging
import os

_logger = logging.getLogger(__name__)

class Validation(models.Model):
  """
  Define las convalidaciones
  """
  _name = 'atenea.validation'
  _description = 'Convalidaciones'

  student_id = fields.Many2one('atenea.student', string = 'Estudiante')
  course_id = fields.Many2one('atenea.course', string = 'Ciclo', required = True)
  validation_subjects_ids = fields.One2many('atenea.validation_subject', 'validation_id', string = 'Módulos que se solicita convalidar', )
  
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
      ], string ='Estado de la convalidación', default = '0')
  
  # fecha de solicitud de la subsanación
  correction_date = fields.Date()

  correction_reason = fields.Selection([
    ('SNF', 'Documento no firmado digitalmente'),
    ('RL', 'No se aporta curso de riesgo laborales > 30h'),
    ('EXP', 'No se aporta expediente académico'),
    ], string ='Razón de la subsanación', default = 'SNF',
    help = "Permite indicar el motivo por el que se solicita la subsanación")