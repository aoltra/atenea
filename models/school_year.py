# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields
from odoo.exceptions import ValidationError

class SchoolYear(models.Model):
  """
  Define información del curso escolar
  """
      
  _name = 'atenea.school_year'
  _description = 'Curso escolar'

  name = fields.Char(readonly = True, compute = '_compute_name', string = 'Curso')
  date_init = fields.Date(string='Fecha de incio oficial')

  # estructura de datos con las fechas 
  dates = { 'init_lective': { 'date': '', 'desc': 'Inicio clases', 'type': 'G'}}

  # inicio real de las clases
  date_init_lective = fields.Date(string = 'Fecha de inicio real', compute = '_compute_date_init_lective', readonly = False)
  # jornadas de bienvenida
  date_welcome_day = fields.Date(string = 'Jornadas de bienvenida', compute = '_compute_welcome_day')
  # fin de las clases de la primera evaluación de segundo
  date_1term2_end = fields.Date(string = 'Fin clases primera evaluación', compute = '_compute_1term2_end', readonly = False) 
  # inicio examenes 1 evaluación de segundo
  date_1term2_exam_ini = fields.Date(string = 'Inicio exámenes primera evaluación', compute = '_compute_1term2_exam_ini') 
  # fin exámenes 1 evaluación de segundo
  date_1term2_exam_end = fields.Date(string = 'Fin exámenes primera evaluación', compute = '_compute_1term2_exam_end') 

  # report  
  school_calendar = fields.Binary(readonly = True)


  # la fecha de inicio no puede ser fin de semana
  @api.constrains('date_init')
  def _check_date_init(self):
    for record in self:
      if record.date_init.weekday() == 5 or record.date_init.weekday() == 6:
        raise ValidationError('La fecha de inicio no puede ser fin de semana')

  @api.depends('date_init')
  def _compute_name(self):
    for record in self:
      if record.date_init == False:
        record.name = ''
      else:
        record.name = '%s/%s' % (record.date_init.year, record.date_init.year + 1)

  @api.depends('date_init')
  def _compute_date_init_lective(self):
    for record in self:
      if record.date_init == False:
        record.date_init_lective = ''
      elif record.date_init.weekday() >= 2 or record.date_init.weekday() <= 4:
        record.date_init_lective = record.date_init + datetime.timedelta(days = 7 - record.date_init.weekday())
  
  @api.depends('date_init_lective')
  def _compute_1term2_end(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_1term2_end = ''
      else: 
        record.date_1term2_end = record.date_init_lective + datetime.timedelta(weeks=9) + datetime.timedelta(days=4)

  @api.depends('date_1term2_end')
  def _compute_1term2_exam_ini(self):
    for record in self:
      if record.date_1term2_end == False:
        record.date_1term2_exam_ini = ''
      else: 
        record.date_1term2_exam_ini = record.date_1term2_end + datetime.timedelta(days=3)

  @api.depends('date_1term2_exam_ini')
  def _compute_1term2_exam_end(self):
    for record in self:
      if record.date_1term2_exam_ini == False:
        record.date_1term2_exam_end = ''
      else: 
        record.date_1term2_exam_end = record.date_1term2_exam_ini + datetime.timedelta(days=4)

  @api.depends('date_init_lective')
  def _compute_welcome_day(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_welcome_day = ''
      else: 
        record.date_welcome_day = record.date_init_lective - datetime.timedelta(days=4)


  """
  https://www.daniweb.com/programming/software-development/code/463551/another-look-at-easter-dates-python
  """
  def _calc_easter(year):
    '''
    Gauss algorithm to calculate the date of easter in a given year
    note // forces integer division in Python3
    returns a date object
    '''
    month = 3
    # determine the Golden number
    golden = (year % 19) + 1
    # determine the century number
    century = year // 100 + 1
    # correct for the years who are not leap years
    xx = (3 * century) // 4 - 12
    # moon correction
    yy = (8 * century + 5) // 25 - 5
    # find Sunday
    zz = (5 * year) // 4 - xx - 10
    # determine epact
    # age of moon on January 1st of that year
    # (follows a cycle of 19 years)
    ee = (11 * golden + 20 + yy - xx) % 30
    if ee == 24:
      ee += 1
    if ee == 25 and golden > 11:
      ee += 1
    # get the full moon
    moon = 44 - ee
    if moon < 21:
      moon += 30
    # up to Sunday
    day = (moon + 7) - ((zz + moon) % 7)
    # possibly up a month in easter_date
    if day > 31:
      day -= 31
      month = 4

    return datetime.datetime(year, month, day)

  "Calcula los dias entre dos fechas, pero si cambia de mes, sólo hasta final o principio de ese mes"
  def _calc_dur(dateI, dateE):
    if dateI.month == dateE.month:
      return (dateE-dateI).days
    else:
      if dateI < dateE:
        return (datetime.datetime(dateI.year, dateI.month, 31) - dateI).days + 1
      else:
        return (datetime.datetime(dateI.year, dateI.month, 1) - dateI).days - 1
      


  def update_dates(self):
    self.dates['init_lective'] = { 
      'date': self.date_init_lective,
      'desc': self._fields['date_init_lective'].string, 
      'type': 'G'
    }

    self.dates['1term2_end'] = { 
      'date': self.date_1term2_end,
      'desc': self._fields['date_1term2_end'].string, 
      'type': 'S'
    }

    self.dates['date_1term2_exam_end'] = { 
      'date': self.date_1term2_exam_end,
      'desc': self._fields['date_1term2_exam_end'].string, 
      'type': 'S'
    }

    self.dates['date_1term2_exam_ini'] = { 
      'date': self.date_1term2_exam_ini,
      'desc': self._fields['date_1term2_exam_ini'].string, 
      'type': 'S',
      'dur': self.date_1term2_exam_end - self.date_1term2_exam_ini + datetime.timedelta(days = 1)
    }

    self.dates['date_welcome_day'] = { 
    'date': self.date_welcome_day, 
    'desc': self._fields['date_welcome_day'].string,
    'type': 'G'
  }