# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SubjectClassroomRel(models.Model): 
  """
  Se crea para dar soporte al campo course
  """
  _name = 'atenea.subject_classroom_rel' 
  _description = 'Relación entre classroom y subject' 
  _rec_name = 'subject_and_course'

  classroom_id = fields.Many2one('atenea.classroom', required = True, string = 'Aula virtual') 
  subject_id = fields.Many2one('atenea.subject', required = True, string = 'Módulo') 

  # ciclo del módulo en el que está asociada el aula
  course_id = fields.Many2one('atenea.course', required = True, string = 'Ciclo')

  subject_and_course = fields.Char(compute = '_compute_subject_and_course', string = 'Módulo (Ciclo)')

  _sql_constraints = [ 
    ('unique_subject_classroom_rel', 'unique(classroom_id, subject_id, course_id)', 
       'Sólo puede haber una relación por aula, ciclo y módulo.'),
  ]

  @api.depends('course_id','subject_id')
  def _compute_subject_and_course(self):
    for record in self:
      if record.subject_id.name == False or record.course_id.abbr == False:
        record.subject_and_course = ''
      else:
        record.subject_and_course = f'{record.subject_id.name} ({record.course_id.abbr})'

  @api.onchange('subject_id')
  def change_subject(self):
    self.ensure_one()
    if self.subject_id.courses_ids != False:
      allow_courses = [course.id for course in self.subject_id.courses_ids]
      return {'domain': { 'course_id': [('id','in', allow_courses)]}}