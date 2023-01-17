# -*- coding: utf-8 -*-

from odoo import models, fields

class Rol(models.Model):
    """
    Define los posibles roles del profesorado
    """
      
    _name = 'atenea.rol'
    _description = 'Rol de profesorado'

    _rec_name = 'rol'

    rol = fields.Char('Cargo', size = 5, required = True)
    description = fields.Char('Descripción')
    course_id = fields.Many2one('atenea.course', 'Ciclo')
    
    