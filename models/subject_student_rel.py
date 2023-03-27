# -*- coding: utf-8 -*-

from odoo import models, fields


class SubjectStudentRel(models.Model): 
  """
  Se crea para dar soporte a un campo intermedio
  """
  _name = 'atenea.subject_student_rel' 
  _description = 'Relación entre student y subject' 

  student_id = fields.Many2one('atenea.student') 
  subject_id = fields.Many2one('atenea.subject') 

  # ciclo en el que está matriculado
  course_id = fields.Many2one('atenea.course')

  # número que determina los flags asociados al estado del record
  status_flags = fields.Integer(default = 0) 

