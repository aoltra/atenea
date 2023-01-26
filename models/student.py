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

  nia = fields.Char(string = 'NIA', size = 9, required = True)
  name = fields.Char(string = 'Nombre', required = True)
  surname = fields.Char(string = 'Apellidos', required = True)
  email = fields.Char(string = 'Email')

  validations_ids = fields.One2many('atenea.validation', 'student_id')