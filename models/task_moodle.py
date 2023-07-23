# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class TaskMoodle(models.Model):
  """
  Define una tarea de moodle que comunica con Atenea. No permite que en una misma aula virtual
  existan dos tareas con la misma key
  """

  _name = 'atenea.task_moodle'
  _description = 'Tarea de Moodle'

  moodle_id = fields.Integer('Identificador Moodle', required = True)
  key = fields.Char('Clave', required = True, help = 'Clave de búsqueda. Tiene que ser única para cada tarea y aula')
  classroom_id = fields.Many2one('atenea.classroom') 
  description = fields.Char('Descripción de la tarea')
  course_abbr = fields.Char(string = 'Ciclo', size = 5)
  
  _sql_constraints = [ 
    ('unique_key', 'unique(key, classroom_id)', 'La clave de búsqueda tiene que ser única para cada tarea y aula.'),
    ('unique_moodle_id', 'unique(moodle_id)', 'El identificador de moodle tiene que ser único.'),
  ]