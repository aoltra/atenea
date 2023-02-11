# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

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
  date_init_lective = fields.Date(string = 'Fecha de inicio real', compute = '_compute_date_init_lective', readonly = False, store = True)
  # jornadas de bienvenida
  date_welcome_day = fields.Date(string = 'Jornadas de bienvenida', compute = '_compute_welcome_day', store = True)
  # fin de las clases de la primera evaluación de segundo
  date_1term2_end = fields.Date(string = 'Fin clases primera evaluación', compute = '_compute_1term2_end', readonly = False, store = True) 
  # inicio examenes 1 evaluación de segundo. En caso de readonly True hay que forzar su grabación en el XML con force_save
  date_1term2_exam_ini = fields.Date(string = 'Inicio exámenes primera evaluación', compute = '_compute_1term2_exam_ini', store = True) 
  # fin exámenes 1 evaluación de segundo
  date_1term2_exam_end = fields.Date(string = 'Fin exámenes primera evaluación', compute = '_compute_1term2_exam_end', store = True) 

  holidays_ids = fields.One2many('atenea.holiday', 'school_year_id')

  # report calendario escolar  
  school_calendar_version = fields.Integer(string = 'Versión calendario escolar', default = 1, store = True, readonly = True)
  school_calendar_update_keys = ['init_lective', 'date_init_lective', 'date_welcome_day', 'date_1term2_end', 'date_1term2_exam_ini', 'date_1term2_exam_end']

  """ Sobreescritura de la función create que es llamada cuando se crea un registro nuevo """
  @api.model
  def create(self, vals):
    # la primera versión de los informes se crea al crear el registro
    vals['school_calendar_version'] = 1
    res_id = super(SchoolYear, self).create(vals)
    return res_id

  """ Sobreescritura de la función write que es llamada cuando se actualiza un registro """
  def write(self, vals):
    # Si alguno de los valores que se han cambiado están en la lista de cambios que afectan al calendario
    if any([i in vals for i in self.school_calendar_update_keys]):
      vals['school_calendar_version'] = self.school_calendar_version + 1

    super(SchoolYear, self).write(vals)

    return True

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
      elif record.date_init.weekday() >= 2:
        record.date_init_lective = record.date_init + datetime.timedelta(days = 7 - record.date_init.weekday())
      else:
        record.date_init_lective = record.date_init

  @api.constrains('date_init_lective')
  def _check_date_init_lective(self):
    for record in self:
      if record.date_init_lective.weekday() >= 4:
        raise ValidationError('La fecha de inicio lectiva no puede ser ni viernes ni fin de semana')
  
  @api.depends('date_init_lective')
  def _compute_1term2_end(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_1term2_end = ''
      else: 
        record.date_1term2_end = record.date_init_lective + datetime.timedelta(weeks=9) + datetime.timedelta(days = 4 - record.date_init_lective.weekday())

  @api.constrains('date_1term2_end')
  def _check_date_1term2_end(self):
    for record in self:
      if record.date_init.weekday() == 5 or record.date_init.weekday() == 6:
        raise ValidationError('La fecha de fin de evaluación no puede ser fin de semana')
             
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

  @api.onchange('date_init')
  def _calculate_holidays(self):
    for record in self:
      # si el año anterior es igual al que se acaba de cambiar no se hace nada
      if self._origin.date_init.year == record.date_init.year:
        continue

      # añade nuevos registro, pero los mantiene en "el aire" hasta que se grabe el school_year
      record.holidays_ids = [(0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Constitución', 
        'date': datetime.datetime(record.date_init.year, 12, 6), 
        'date_end': datetime.datetime(record.date_init.year, 12, 6) })]  


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

    self.dates['date_1term2_exam_ini'] = { 
      'date': self.date_1term2_exam_ini,
      'desc': self._fields['date_1term2_exam_ini'].string, 
      'type': 'S',
      # días que dura este evento, además del día indicado
      'dur': self.date_1term2_exam_end - self.date_1term2_exam_ini
    }

    self.dates['date_1term2_exam_end'] = { 
      'date': self.date_1term2_exam_end,
      'desc': self._fields['date_1term2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_1term2_exam_ini - self.date_1term2_exam_end,
    }

    self.dates['date_welcome_day'] = { 
    'date': self.date_welcome_day, 
    'desc': self._fields['date_welcome_day'].string,
    'type': 'G'
  }
