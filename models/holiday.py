# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import ValidationError

class Holiday(models.Model):
  """
  Define un dia o un conjunto de dias consecutivos de fiesta
  """

  _name = 'atenea.holiday'
  _description = 'Días de fiesta'
  _order = 'date'
  _rec_name = 'description'

  school_year_id = fields.Many2one('atenea.school_year', string = 'Curso escolar')
  date = fields.Date(string = 'Dia', required = True) 
  date_end = fields.Date(string = 'Fin de fiesta', required = True, default = None) 
  duration = fields.Integer(string = "Duración", compute = '_compute_duration')
  description = fields.Char('Descripción', required = True)

  @api.depends('date', 'date_end')
  def _compute_duration(self):
    for record in self:
      record.duration = (record.date_end - record.date).days + 1

  # la fecha de fin tiene que ser posterior a la de inicio
  @api.constrains('date', 'date_end')
  def _check_date(self):
    for record in self:
      if record.date_end != None:
        if record.date == None or record.date > record.date_end:
          raise ValidationError('La fecha de fin tiene que ser mayor que la de inicio')
