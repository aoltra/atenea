from odoo import models, fields

class Subject(models.Model):
    """
    Define un módulo
    """
      
    _name = 'atenea.subject'
    _description = 'Módulo de un ciclo formativo'

    abbr = fields.Char(size = 4, required = True, translate = True)
    code = fields.Char(size = 4, required = True)
    name = fields.Char(required = True, translate = True)

    courses_ids = fields.Many2many('atenea.course')