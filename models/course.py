# -*- coding: utf-8 -*-

from odoo import models, fields

class Course(models.Model):
    """
    Define un ciclo formativo
    """

    _name = 'atenea.course'
    _description = 'Ciclo Formativo'

    abbr = fields.Char('Abreviatura', size = 5,required = True, translate=True)
    name = fields.Char('Ciclo', required = True, translate=True)
    code = fields.Char('Código', required = True, size = 6)

    subjects_ids = fields.Many2many('atenea.subject', string = 'Módulos')
    students_ids = fields.Many2many('atenea.student')
    roles_ids = fields.One2many('atenea.rol', 'course_id')