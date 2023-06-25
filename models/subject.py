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

    courses_ids = fields.Many2many('atenea.course', string = 'Ciclos')
    validations_ids = fields.One2many('atenea.validation_subject', 'subject_id')
    classroom_id = fields.Many2one('atenea.classroom', string = 'Aula virtual')
    students_ids = fields.Many2many(
        'atenea.student', 
        string = 'Estudiante',
        relation = 'subject_student_rel', 
        column1 = 'subject_id', column2 = 'student_id')