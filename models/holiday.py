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

  school_year_id = fields.Many2one('atenea.school_year', string = 'Curso escolar', ondelete = 'cascade')
  description = fields.Char(required = True, string = "Descripción")
  date = fields.Date(string = 'Dia', required = True) 
  date_end = fields.Date(string = 'Fin de fiesta', required = True, compute='_compute_date_end', store = True, readonly = False) 
  duration = fields.Integer(string = "Duración", compute = '_compute_duration')

  # key para la selección del festivo
  key = fields.Char()
  
  @api.depends('date', 'date_end')
  def _compute_duration(self):
    for record in self:
      if record.date_end != False and record.date != False:
        record.duration = (record.date_end - record.date).days + 1
      else:
        record.duration = 1

  @api.depends('date')
  def _compute_date_end(self):
    for record in self:
      if record.date_end == False: # si no hay fecha final definida
        record.date_end = record.date
      else:
        record.date_end = record.date_end

  # la fecha de fin tiene que ser posterior a la de inicio
  @api.constrains('date', 'date_end')
  def _check_date(self):
    for record in self:
      if record.date_end != False:
        if record.date > record.date_end:
          raise ValidationError('[Festivos]: la fecha de fin tiene que ser mayor que la de inicio en el festivo {}'.format(record.description))
