# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import ValidationError

class Student(models.Model):
  """
  Define un estudiante
  """

  _name = 'atenea.student'
  _description = 'Estudiante'
  _order = 'surname'

  moodle_id = fields.Char(string = 'moodle_id', size = 9, required = True)
  nia = fields.Char(string = 'NIA', size = 9)
  name = fields.Char(string = 'Nombre', required = True)
  surname = fields.Char(string = 'Apellidos', required = True)
  email = fields.Char(string = 'Email')

  # un estudiante podría solicitar convalidaciones de dos ciclos diferentes 
  # (aunque a día de hoy no está permitido)
  validations_ids = fields.One2many('atenea.validation', 'student_id')
  subjects_ids = fields.Many2many('atenea.subject',
    string = 'Módulo',
    relation = 'subject_student_rel', 
    column1 = 'student_id', column2 = 'subject_id')