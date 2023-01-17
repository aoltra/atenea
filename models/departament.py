# -*- coding: utf-8 -*-

from odoo import models, fields

class Departament(models.Model):
    """
    Define los departamentos didácticos
    """
      
    _name = 'atenea.departament'
    _description = 'Departamento didáctico'

    name = fields.Char('Departamento', required=True)
    roles_ids = fields.One2many('atenea.rol', 'departament_id')
