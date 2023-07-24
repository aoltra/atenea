from odoo import api, models, fields

class Subject(models.Model):
    """
    Define un módulo
    """
      
    _name = 'atenea.subject'
    _description = 'Módulo de un ciclo formativo'

    abbr = fields.Char(size = 4, required = True, translate = True, string = "Abreviatura")
    code = fields.Char(size = 6, required = True, string = "Código")
    name = fields.Char(required = True, translate = True, string = "Nombre")
    year = fields.Selection([('1', '1º'), ('2', '2º')], required = True, default = '1', string = 'Curso')

    courses_ids = fields.Many2many('atenea.course', string = 'Ciclos', help = 'Ciclos en los que se imparte')
    validations_ids = fields.One2many('atenea.validation_subject', 'subject_id')

    classrooms_ids = fields.One2many('atenea.subject_classroom_rel', 'subject_id', string = 'Aulas virtuales')
  
    students_ids = fields.Many2many(
      'atenea.student', 
      string = 'Estudiante',
      relation = 'subject_student_rel', 
      column1 = 'subject_id', column2 = 'student_id')
    
    def get_classroom_by_course_id(self, course):
      """
      Devuleve el aula virtual asociada a este módulo para un ciclo determinado
      """
      self.ensure_one()
      
      return self.classrooms_ids.filtered(lambda t: t.course_id.id == course.id)['classroom_id']
    