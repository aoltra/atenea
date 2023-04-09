# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields
from odoo.exceptions import ValidationError
import toolz
import logging

_logger = logging.getLogger(__name__)

class SchoolYear(models.Model):
  """
  Define información del curso escolar
  """
      
  _name = 'atenea.school_year'
  _description = 'Curso escolar'

  name = fields.Char(readonly = True, compute = '_compute_name', string = 'Curso')
  state = fields.Selection([
      ('0', 'Borrador'),
      ('1', 'En curso'),
      ('2', 'Finalizado')
      ], string ='Estado del curso', default = '1') # TODO OJO!! hay que cambiarlo a 0
  
  date_init = fields.Date(string='Fecha de inicio oficial')

  # estructura de datos con las fechas 
  dates = { 'init_lective': { 'date': '', 'desc': 'Inicio clases', 'type': 'G'}}

  # inicio real de las clases
  date_init_lective = fields.Date(string = 'Fecha de inicio real', compute = '_compute_date_init_lective', readonly = False, store = True)
  # jornadas de bienvenida
  date_welcome_day = fields.Date(string = 'Jornadas de bienvenida', compute = '_compute_welcome_day', store = True)
  # SEGUNDO
  # inicio primera evaluación
  date_1term2_ini = fields.Date(string = 'Inicio primera evaluación', compute = '_compute_1term2_ini') 
  # fin de las clases de la primera evaluación de segundo
  date_1term2_end = fields.Date(string = 'Fin clases primera evaluación', compute = '_compute_1term2_end', readonly = False, store = True) 
  # inicio examenes 1 evaluación de segundo. En caso de readonly True hay que forzar su grabación en el XML con force_save
  date_1term2_exam_ini = fields.Date(string = 'Inicio exámenes primera evaluación', compute = '_compute_1term2_exam_ini', readonly = False, store = True) 
  # fin exámenes 1 evaluación de segundo
  date_1term2_exam_end = fields.Date(string = 'Fin exámenes primera evaluación', compute = '_compute_1term2_exam_end', store = True) 
  # duración primera evaluación segundo
  duration_1term2 = fields.Integer(string = 'Duración (semanas)', compute = '_compute_duration_1term2')
  # inicio segunda evaluación
  date_2term2_ini = fields.Date(string = 'Inicio segunda evaluación', compute = '_compute_2term2_ini', store = True) 
  # fin de las clases de la segunda evaluación de segundo
  date_2term2_end = fields.Date(string = 'Fin clases segunda evaluación', compute = '_compute_2term2_end', readonly = False, store = True) 
  # inicio examenes 2 evaluación de segundo
  date_2term2_exam_ini = fields.Date(string = 'Inicio exámenes segunda evaluación', compute = '_compute_2term2_exam_ini', readonly = False, store = True) 
  # fin exámenes 2 evaluación de segundo
  date_2term2_exam_end = fields.Date(string = 'Fin exámenes segunda evaluación', compute = '_compute_2term2_exam_end', store = True) 
  # duración segunda evaluación segundo
  duration_2term2 = fields.Integer(string = 'Duración (semanas)', compute = '_compute_duration_2term2')
  # inicio examenes ordinaria de segundo
  date_ord2_exam_ini = fields.Date(string = 'Inicio exámenes ordinaria', compute = '_compute_ord2_exam_ini', readonly = False, store = True) 
  # fin exámenes ordinaria de segundo
  date_ord2_exam_end = fields.Date(string = 'Fin exámenes ordinaria', compute = '_compute_ord2_exam_end', store = True) 
  # inicio examenes extraordinaria de segundo
  date_extraord2_exam_ini = fields.Date(string = 'Inicio exámenes extraordinaria', compute = '_compute_extraord2_exam_ini', readonly = False, store = True) 
  # fin exámenes extraordinaria de segundo
  date_extraord2_exam_end = fields.Date(string = 'Fin exámenes extraordinaria', compute = '_compute_extraord2_exam_end', store = True) 
  # anulación de matrícula
  date_cancellation2 = fields.Date(string = 'Fin anulación de matrícula', compute = '_compute_cancellation2') 
  # renuncia convocatoria ordinaria
  date_waiver_ord2 = fields.Date(string = 'Fin renuncia convocatoria ordinaria', compute = '_compute_waiver_ord2') 
  # renuncia convocatoria extraordinaria
  date_waiver_extraord2 = fields.Date(string = 'Fin renuncia convocatoria extraordinaria', compute = '_compute_waiver_extraord2') 

  # PRIMERO
  # fin de las clases de la primera evaluación de primero
  date_1term1_end = fields.Date(string = 'Fin clases primera evaluación', compute = '_compute_1term1_end', readonly = False, store = True) 
  # inicio examenes 1 evaluación de segundo. En caso de readonly True hay que forzar su grabación en el XML con force_save
  date_1term1_exam_ini = fields.Date(string = 'Inicio exámenes primera evaluación', compute = '_compute_1term1_exam_ini', readonly = False, store = True) 
  # fin exámenes 1 evaluación de primero
  date_1term1_exam_end = fields.Date(string = 'Fin exámenes primera evaluación', compute = '_compute_1term1_exam_end', store = True) 
  # duración primera evaluación primero
  duration_1term1 = fields.Integer(string = 'Duración (semanas)', compute = '_compute_duration_1term1')
  # inicio segunda evaluación primero
  date_2term1_ini = fields.Date(string = 'Inicio segunda evaluación', compute = '_compute_2term1_ini', store = True) 
  # fin de las clases de la segunda evaluación de primero
  date_2term1_end = fields.Date(string = 'Fin clases segunda evaluación', compute = '_compute_2term1_end', readonly = False, store = True) 
  # inicio examenes 2 evaluación de primero
  date_2term1_exam_ini = fields.Date(string = 'Inicio exámenes segunda evaluación', compute = '_compute_2term1_exam_ini', readonly = False, store = True) 
  # fin exámenes 2 evaluación de primero
  date_2term1_exam_end = fields.Date(string = 'Fin exámenes segunda evaluación', compute = '_compute_2term1_exam_end', store = True) 
  # duración segunda evaluación primero
  duration_2term1 = fields.Integer(string = 'Duración (semanas)', compute = '_compute_duration_2term1')
  # inicio examenes ordinaria de primero
  date_ord1_exam_ini = fields.Date(string = 'Inicio exámenes ordinaria', compute = '_compute_ord1_exam_ini', readonly = False, store = True) 
  # fin exámenes ordinaria de primero
  date_ord1_exam_end = fields.Date(string = 'Fin exámenes ordinaria', compute = '_compute_ord1_exam_end', store = True) 
  # inicio exámenes extraordinaria de primero
  date_extraord1_exam_ini = fields.Date(string = 'Inicio exámenes extraordinaria', compute = '_compute_extraord1_exam_ini', readonly = False, store = True) 
  # fin exámenes extraordinaria de segundo
  date_extraord1_exam_end = fields.Date(string = 'Fin exámenes extraordinaria', compute = '_compute_extraord1_exam_end', store = True) 
  # anulación de matrícula primero
  date_cancellation1 = fields.Date(string = 'Fin anulación de matrícula', compute = '_compute_cancellation1') 
  # renuncia convocatoria ordinaria primero
  date_waiver_ord1 = fields.Date(string = 'Fin renuncia convocatoria ordinaria', compute = '_compute_waiver_ord1') 
  # renuncia convocatoria extraordinaria primero
  date_waiver_extraord1 = fields.Date(string = 'Fin renuncia convocatoria extraordinaria', compute = '_compute_waiver_extraord1') 

  # PFC
  date_2term_pfc_exposition_ini = fields.Date(string = 'Inicio periodo de defensas', compute = '_compute_2term_pfc_exposition_ini', readonly = False) 
  date_2term_pfc_exposition_end = fields.Date(string = 'Fin periodo de defensas', compute = '_compute_2term_pfc_exposition_end') 
  date_1term_pfc_exposition_ini = fields.Date(string = 'Inicio periodo de defensas', compute = '_compute_1term_pfc_exposition_ini', readonly = False) 
  date_1term_pfc_exposition_end = fields.Date(string = 'Fin periodo de defensas', compute = '_compute_1term_pfc_exposition_end')
  date_2term_pfc_delivery =  fields.Date(string = 'Entrega documentación', compute = '_compute_2term_pfc_delivery', readonly = False) 
  date_1term_pfc_delivery =  fields.Date(string = 'Entrega documentación', compute = '_compute_1term_pfc_delivery', readonly = False) 
  date_2term_pfc_waiver =  fields.Date(string = 'Fin renuncia a la convocatoria', compute = '_compute_2term_pfc_waiver') 
  date_1term_pfc_waiver =  fields.Date(string = 'Fin renuncia a la convocatoria', compute = '_compute_1term_pfc_waiver') 
  date_2term_pfc_cancellation =  fields.Date(string = 'Fin anulación matrícula (registro)', compute = '_compute_2term_pfc_cancellation') 
  date_1term_pfc_cancellation =  fields.Date(string = 'Fin anulación matrícula (registro)', compute = '_compute_1term_pfc_cancellation') 
  date_1term_pfc_talk = fields.Date(string = 'Charla informativa', compute = '_compute_1term_pfc_talk') 
  date_2term_pfc_talk = fields.Date(string = 'Charla informativa', compute = '_compute_2term_pfc_talk') 
  date_2term_pfc_proposal1 = fields.Date(string = 'Entrega propuesta', compute = '_compute_2term_pfc_proposal', readonly = False) 
  date_1term_pfc_proposal1 = fields.Date(string = 'Entrega propuesta', compute = '_compute_1term_pfc_proposal', readonly = False) 
  date_2term_pfc_proposal2= fields.Date(string = 'Entrega propuesta corregidas', compute = '_compute_2term_pfc_fixed_proposal') 
  date_1term_pfc_proposal2 = fields.Date(string = 'Entrega propuesta corregidas', compute = '_compute_1term_pfc_fixed_proposal') 


  holidays_ids = fields.One2many('atenea.holiday', 'school_year_id')
  cron_ids = fields.One2many('atenea.ir.cron', 'school_year_id') #, domain = 'self._get_school_year_id')

  # report calendario escolar  
  school_calendar_version = fields.Integer(string = 'Versión calendario escolar', default = 1, store = True, readonly = True)
  school_calendar_update_keys = ['init_lective', 'date_init_lective', 'date_welcome_day', 'date_1term2_end', 
    'date_1term2_exam_ini', 'date_1term2_exam_end', 'date_2term2_ini', 'date_2term2_end', 'date_ord2_exam_ini',
    'date_ord2_exam_end','date_extraord2_exam_ini', 'date_extraord2_exam_end', 
    'date_1term1_end', 'date_1term1_exam_ini', 'date_1term1_exam_end', 'date_2term1_ini', 'date_2term1_end', 
    'date_ord1_exam_ini', 'date_ord1_exam_end','date_extraord1_exam_ini', 'date_extraord1_exam_end', 'state']
  
  pfc_calendar_version = fields.Integer(string = 'Versión calendario PFC', default = 1, store = True, readonly = True)
  pfc_calendar_update_keys = ['date_2term_exposition_ini']

  validations_ids = fields.One2many('atenea.validation', 'school_year_id')

  # TODO: constraints para que se mantenga el orden cronológico de las fechas

  """ Sobreescritura de la función create que es llamada cuando se crea un registro nuevo """
  @api.model
  def create(self, vals):
    # la primera versión de los informes se crea al crear el registro
    vals['school_calendar_version'] = 1
    res_id = super(SchoolYear, self).create(vals)
    return res_id

  """ Sobreescritura de la función write que es llamada cuando se actualiza un registro """
  def write(self, vals):
    ref = self.env.ref
    # Si alguno de los valores que se han cambiado están en la lista de cambios que afectan al calendario
    # y el curso está 'en curso'
    if any([i in vals for i in self.school_calendar_update_keys]) and \
      (self.state == '1' or ('state' in vals and vals['state'] == '1')):
      vals['school_calendar_version'] = self.school_calendar_version + 1

    if any([i in vals for i in self.pfc_calendar_update_keys]) and \
      (self.state == '1' or ('state' in vals and vals['state'] == '1')):
      vals['pfc_calendar_version'] = self.pfc_calendar_version + 1

    super(SchoolYear, self).write(vals)

    return True
  
  # ###########
  # GENERALES
  # ###########

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
  def _compute_welcome_day(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_welcome_day = ''
      else: 
        record.date_welcome_day = record.date_init_lective - datetime.timedelta(days = 4)

  # ###########
  # SEGUNDO
  # ###########

  @api.depends('date_init_lective')
  def _compute_1term2_ini(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_1term2_ini = ''
      else: 
        record.date_1term2_ini = record.date_init_lective

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
      if record.date_1term2_end.weekday() == 5 or record.date_1term2_end.weekday() == 6:
        raise ValidationError('La fecha de fin de evaluación no puede ser fin de semana')

  @api.depends('date_1term2_end','date_init_lective')    
  def _compute_duration_1term2(self):
    for record in self:
      if record.date_1term2_end != False and record.date_init_lective != False:
        record.duration_1term2 = (record.date_1term2_end - record.date_init_lective).days // 7 + 1
      else:
        record.duration_1term2 = 0
             
  @api.depends('date_1term2_end', 'holidays_ids.date')
  def _compute_1term2_exam_ini(self):
    for record in self:
      if record.date_1term2_end == False:
        record.date_1term2_exam_ini = ''
      else: 
        record.date_1term2_exam_ini = record.date_1term2_end + datetime.timedelta(days=3)

      # obtener los festivos del día de la constitucion e inmaculada
      constitucion_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'constitucion'), None)
      inma_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'inmaculada'), None)
   
      if constitucion_holiday == None or inma_holiday == None:
        continue
      # si en la semana de exámenes está el día 6/12 o el 8/12, retraso los exámenes una semana
      elif (constitucion_holiday.date >= record.date_1term2_exam_ini and constitucion_holiday.date < record.date_1term2_exam_end) or \
        (inma_holiday.date >= record.date_1term2_exam_ini and inma_holiday.date < record.date_1term2_exam_end):
        record.date_1term2_exam_ini = record.date_1term2_exam_ini + datetime.timedelta(weeks = 1)
        record.date_1term2_exam_end = record.date_1term2_exam_end + datetime.timedelta(weeks = 1)
        record.date_1term2_end = record.date_1term2_end + datetime.timedelta(weeks = 1)

  @api.constrains('date_1term2_exam_ini')
  def _check_date_1term2_exam_ini(self):
    for record in self:
      if record.date_1term2_exam_ini.weekday() != 0:
        raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_1term2_exam_ini')
  def _compute_1term2_exam_end(self):
    for record in self:
      if record.date_1term2_exam_ini == False:
        record.date_1term2_exam_end = ''
      else: 
        record.date_1term2_exam_end = record.date_1term2_exam_ini + datetime.timedelta(days=4)

  @api.depends('date_1term2_exam_end')
  def _compute_2term2_ini(self):
    for record in self:
      if record.date_1term2_exam_end == False:
        record.date_2term2_ini = ''
      else: 
        record.date_2term2_ini = record.date_1term2_exam_end + datetime.timedelta(days = 3)

  @api.depends('date_2term2_ini', 'duration_1term2')
  def _compute_2term2_end(self):
    for record in self:
      if record.date_2term2_ini == False:
        record.date_2term2_end = ''
      else:
        # 20 + 2 (ya que Navidad al final son siempre dos semanas no lectivas). 
        # Eso lo ubica al principio de la semana 21, asi que -1 y sumanos para alcanzar el viernes 
        record.date_2term2_end = record.date_2term2_ini + datetime.timedelta(weeks = 21 - record.duration_1term2) + datetime.timedelta(days = 4)
      
  @api.constrains('date_2term2_end')
  def _check_date_2term2_end(self):
    for record in self:
      if record.date_2term2_end.weekday() == 5 or record.date_2term2_end.weekday() == 6:
        raise ValidationError('La fecha de fin de evaluación no puede ser fin de semana')

  @api.depends('date_2term2_end','date_2term2_ini')    
  def _compute_duration_2term2(self):
    for record in self:
      if record.date_2term2_end != False and record.date_2term2_ini != False:
        record.duration_2term2 = (record.date_2term2_end - record.date_2term2_ini).days // 7 + 1 - 2 # - 2 por la dos de navidad 
      else:
        record.duration_2term2 = 0
             
  @api.depends('date_2term2_end')
  def _compute_2term2_exam_ini(self):
    for record in self:
      if record.date_2term2_end == False:
        record.date_2term2_exam_ini = ''
      else: 
        record.date_2term2_exam_ini = record.date_2term2_end + datetime.timedelta(days=3)

  @api.constrains('date_2term2_exam_ini')
  def _check_date_2term2_exam_ini(self):
    for record in self:
      if record.date_2term2_exam_ini != False: 
        if record.date_2term2_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_2term2_exam_ini')
  def _compute_2term2_exam_end(self):
    for record in self:
      if record.date_2term2_exam_ini == False:
        record.date_2term2_exam_end = ''
      else: 
        record.date_2term2_exam_end = record.date_2term2_exam_ini + datetime.timedelta(days=4)

  @api.depends('date_2term2_exam_ini')
  def _compute_ord2_exam_ini(self):
    for record in self:
      if record.date_2term2_ini == False:
        record.date_ord2_exam_ini = ''
      else: 
        record.date_ord2_exam_ini = record.date_2term2_exam_ini + datetime.timedelta(weeks = 2)

  @api.constrains('date_ord2_exam_ini')
  def _check_date_ord2_exam_ini(self):
    for record in self:
      if record.date_ord2_exam_ini != False: 
        if record.date_ord2_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_ord2_exam_ini')
  def _compute_ord2_exam_end(self):
    for record in self:
      if record.date_ord2_exam_ini == False:
        record.date_ord2_exam_end = ''
      else: 
        record.date_ord2_exam_end = record.date_ord2_exam_ini + datetime.timedelta(days=4)

  @api.depends('date_2term1_exam_ini')
  def _compute_extraord2_exam_ini(self):
    for record in self:
      if record.date_2term2_ini == False:
        record.date_extraord2_exam_ini = ''
      else: 
        record.date_extraord2_exam_ini = record.date_2term1_exam_ini - datetime.timedelta(weeks = 1)

  @api.constrains('date_extraord2_exam_ini')
  def _check_date_extraord2_exam_ini(self):
    for record in self:
      if record.date_extraord2_exam_ini != False: 
        if record.date_extraord2_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_extraord2_exam_ini')
  def _compute_extraord2_exam_end(self):
    for record in self:
      if record.date_extraord2_exam_ini == False:
        record.date_extraord2_exam_end = ''
      else: 
        record.date_extraord2_exam_end = record.date_extraord2_exam_ini + datetime.timedelta(days = 4)
  
  @api.depends('date_ord2_exam_ini')
  def _compute_cancellation2(self):
    for record in self:
      christmas_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'navidad'), None)
      
      if record.date_ord2_exam_ini == False:
        record.date_cancellation2 = ''
      else: 
        record.date_cancellation2 = datetime.datetime(record.date_ord2_exam_ini.year, 1, record.date_ord2_exam_ini.day)
        if christmas_holiday == None:
          continue
        elif (record.date_cancellation2 >= christmas_holiday.date and record.date_cancellation2 <= christmas_holiday.date_end):
          record.date_cancellation2 = christmas_holiday.date_end + datetime.timedelta(days = 1)
        
  @api.depends('date_ord2_exam_ini')
  def _compute_waiver_ord2(self):
    for record in self:
      if record.date_ord2_exam_ini == False:
        record.date_waiver_ord2 = ''      
      else:
        record.date_waiver_ord2 = datetime.datetime(record.date_ord2_exam_ini.year, record.date_ord2_exam_ini.month - 1, record.date_ord2_exam_ini.day)

  @api.depends('date_extraord2_exam_ini')
  def _compute_waiver_extraord2(self):
    for record in self:
      if record.date_extraord2_exam_ini == False:
        record.date_waiver_extraord2 = ''      
      else:
        record.date_waiver_extraord2 = datetime.datetime(record.date_extraord2_exam_ini.year, record.date_extraord2_exam_ini.month - 1, record.date_extraord2_exam_ini.day)

  # ###########
  # PRIMERO
  # ###########
  @api.depends('date_init_lective', 'date_1term1_exam_ini')
  def _compute_1term1_end(self):
    for record in self:
      if record.date_init_lective == False:
        record.date_1term1_end = ''
      else: 
        # 15 + 2 (2 por las semanas de navidad, -1 por que sumo luego los 4 dias hasta el viernes)
        record.date_1term1_end = record.date_init_lective + datetime.timedelta(weeks = 16) + datetime.timedelta(days = 4 - record.date_init_lective.weekday())
        #record.date_1term1_end = record.date_1term1_end + datetime.timedelta(weeks = 1)

      # obtener los festivos de Navidad
      christmas_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'navidad'), None)
      if christmas_holiday == None:
        continue

      if record.date_1term1_exam_ini == False:
         continue

      # si la navidad acaba después de los exámenes 
      # y al menos doy una semana lectiva entre fiestas y examenes
      if (christmas_holiday.date_end.weekday() < 3 and (record.date_1term1_exam_ini - christmas_holiday.date_end).days <= 0) or \
        (christmas_holiday.date_end.weekday() >= 3 and (record.date_1term1_exam_ini - christmas_holiday.date_end).days < 7):
        more_weeks = 0
        if christmas_holiday.date_end.weekday() >= 3 and (record.date_1term1_exam_ini - christmas_holiday.date_end).days <=0:
          more_weeks = (christmas_holiday.date_end - record.date_1term1_exam_ini).days // 7 + 1
        record.date_1term1_exam_ini = record.date_1term1_exam_ini + datetime.timedelta(weeks = 1) + datetime.timedelta(weeks = more_weeks)
        record.date_1term1_exam_end = record.date_1term1_exam_end + datetime.timedelta(weeks = 1) + datetime.timedelta(weeks = more_weeks)
        record.date_1term1_end = record.date_1term1_end + datetime.timedelta(weeks = 1) + datetime.timedelta(weeks = more_weeks)
    
  @api.depends('date_1term1_end', 'holidays_ids.date')
  def _compute_1term1_exam_ini(self):
    for record in self:
      if record.date_1term1_end == False:
        record.date_1term1_exam_ini = ''
      else: 
        record.date_1term1_exam_ini = record.date_1term1_end + datetime.timedelta(days = 3)

        christmas_holiday = next((holiday for holiday in record.holidays_ids if holiday.key == 'navidad'), None)
        if christmas_holiday == None:
          continue

        if (christmas_holiday.date_end.weekday() < 3 and (record.date_1term1_exam_ini - christmas_holiday.date_end).days <= 0) or \
        (christmas_holiday.date_end.weekday() >= 3 and (record.date_1term1_exam_ini - christmas_holiday.date_end).days < 7):
          # en caso de que la fecha de fin de fiestas sea mucho más posterior que la de inicio de exámenes
          more_weeks = 0
          if christmas_holiday.date_end.weekday() >= 3 and (record.date_1term1_exam_ini - christmas_holiday.date_end).days <=0:
            more_weeks = (christmas_holiday.date_end - record.date_1term1_exam_ini).days // 7 + 1

          record.date_1term1_exam_ini = record.date_1term1_exam_ini + datetime.timedelta(weeks = 1 + more_weeks)
          record.date_1term1_end = record.date_1term1_end + datetime.timedelta(weeks = 1 + more_weeks)
  
  @api.constrains('date_1term1_end')
  def _check_date_1term1_end(self):
    for record in self:
      if record.date_1term1_end.weekday() == 5 or record.date_1term1_end.weekday() == 6:
        raise ValidationError('La fecha de fin de evaluación no puede ser fin de semana')

  @api.depends('date_1term1_end','date_init_lective')    
  def _compute_duration_1term1(self):
    for record in self:
      if record.date_1term1_end != False and record.date_init_lective != False:
        record.duration_1term1 = ((record.date_1term1_end - record.date_init_lective).days - 14) // 7 + 1
      else:
        record.duration_1term1 = 0

  @api.constrains('date_1term1_exam_ini')
  def _check_date_1term1_exam_ini(self):
    for record in self:
      if record.date_1term1_exam_ini.weekday() != 0:
        raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_1term1_exam_ini')
  def _compute_1term1_exam_end(self):
    for record in self:
      if record.date_1term1_exam_ini == False:
        record.date_1term1_exam_end = ''
      else: 
        record.date_1term1_exam_end = record.date_1term1_exam_ini + datetime.timedelta(days = 4)
  
  @api.depends('date_1term1_exam_end')
  def _compute_2term1_ini(self):
    for record in self:
      if record.date_1term1_exam_end == False:
        record.date_2term1_ini = ''
      else: 
        record.date_2term1_ini = record.date_1term1_exam_end + datetime.timedelta(days = 3)
        
  @api.depends('date_2term1_ini', 'duration_1term1')
  def _compute_2term1_end(self):
    for record in self:
      if record.date_2term1_ini == False:
        record.date_2term1_end = ''
      else:
        # 30 + 1 (ya que pascua al final es siempre una semana no lectivas) 
        # Eso lo ubica al principio de la semana 31, asi que -1 y sumanos para alcanzar el viernes 
        record.date_2term1_end = record.date_2term1_ini + datetime.timedelta(weeks = 30 - record.duration_1term1) + datetime.timedelta(days = 4)
      
  @api.constrains('date_2term1_end')
  def _check_date_2term1_end(self):
    for record in self:
      if record.date_2term1_end.weekday() == 5 or record.date_2term1_end.weekday() == 6:
        raise ValidationError('La fecha de fin de evaluación no puede ser fin de semana')

  @api.depends('date_2term1_end','date_2term1_ini')
  def _compute_duration_2term1(self):
    for record in self:
      if record.date_2term1_end != False and record.date_2term1_ini != False:
        record.duration_2term1 = (record.date_2term1_end - record.date_2term1_ini).days // 7 + 1 - 1 # - 1 por la dos pascua 
      else:
        record.duration_2term1 = 0
             
  @api.depends('date_2term1_end')
  def _compute_2term1_exam_ini(self):
    for record in self:
      if record.date_2term1_end == False:
        record.date_2term1_exam_ini = ''
      else: 
        record.date_2term1_exam_ini = record.date_2term1_end + datetime.timedelta(days = 3)

  @api.constrains('date_2term1_exam_ini')
  def _check_date_2term1_exam_ini(self):
    for record in self:
      if record.date_2term1_exam_ini != False: 
        if record.date_2term1_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_2term1_exam_ini')
  def _compute_2term1_exam_end(self):
    for record in self:
      if record.date_2term1_exam_ini == False:
        record.date_2term1_exam_end = ''
      else: 
        record.date_2term1_exam_end = record.date_2term1_exam_ini + datetime.timedelta(days=4)
 
  @api.depends('date_2term1_exam_ini')
  def _compute_ord1_exam_ini(self):
    for record in self:
      if record.date_2term1_ini == False:
        record.date_ord1_exam_ini = ''
      else: 
        record.date_ord1_exam_ini = record.date_2term1_exam_ini + datetime.timedelta(weeks = 2)

  @api.constrains('date_ord1_exam_ini')
  def _check_date_ord1_exam_ini(self):
    for record in self:
      if record.date_ord1_exam_ini != False: 
        if record.date_ord1_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_2term1_exam_ini')
  def _compute_ord1_exam_end(self):
    for record in self:
      if record.date_ord1_exam_ini == False:
        record.date_ord1_exam_end = ''
      else: 
        record.date_ord1_exam_end = record.date_ord1_exam_ini + datetime.timedelta(days=4)

  @api.depends('date_ord1_exam_ini')
  def _compute_extraord1_exam_ini(self):
    for record in self:
      if record.date_ord1_exam_ini == False:
        record.date_extraord1_exam_ini = ''
      else: 
        record.date_extraord1_exam_ini = record.date_ord1_exam_ini + datetime.timedelta(weeks = 4)

  @api.constrains('date_extraord1_exam_ini')
  def _check_date_extraord1_exam_ini(self):
    for record in self:
      if record.date_extraord1_exam_ini != False: 
        if record.date_extraord1_exam_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de exámenes tiene que ser un lunes')
  
  @api.depends('date_extraord1_exam_ini')
  def _compute_extraord1_exam_end(self):
    for record in self:
      if record.date_extraord1_exam_ini == False:
        record.date_extraord1_exam_end = ''
      else: 
        record.date_extraord1_exam_end = record.date_extraord1_exam_ini + datetime.timedelta(days = 4)
  
  @api.depends('date_ord1_exam_ini')
  def _compute_cancellation1(self):
    for record in self:
      if record.date_ord1_exam_ini == False:
        record.date_cancellation1 = ''
      else: 
        record.date_cancellation1 = datetime.datetime(record.date_ord1_exam_ini.year, record.date_ord1_exam_ini.month - 2, record.date_ord1_exam_ini.day)
        
  @api.depends('date_ord1_exam_ini')
  def _compute_waiver_ord1(self):
    for record in self:
      if record.date_ord1_exam_ini == False:
        record.date_waiver_ord1 = ''      
      else:
        record.date_waiver_ord1 = datetime.datetime(record.date_ord1_exam_ini.year, record.date_ord1_exam_ini.month - 1, record.date_ord1_exam_ini.day)

  @api.depends('date_extraord1_exam_ini')
  def _compute_waiver_extraord1(self):
    for record in self:
      if record.date_extraord1_exam_ini == False:
        record.date_waiver_extraord1 = ''      
      else:
        record.date_waiver_extraord1 = datetime.datetime(record.date_extraord1_exam_ini.year, record.date_extraord1_exam_ini.month - 1, record.date_extraord1_exam_ini.day)


  # ###########
  # PFC
  # ###########
  @api.depends('date_2term2_exam_ini')
  def _compute_2term_pfc_exposition_ini(self):
    for record in self:
      if record.date_2term2_exam_ini == False:
        record.date_2term_pfc_exposition_ini = ''
      else: 
        record.date_2term_pfc_exposition_ini = record.date_2term2_exam_ini - datetime.timedelta(weeks = 1)

  @api.constrains('date_2term_pfc_exposition_ini')
  def _check_date_2term_pfc_exposition_ini(self):
    for record in self:
      if record.date_2term_pfc_exposition_ini != False: 
        if record.date_2term_pfc_exposition_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de las defensas tiene que ser un lunes')

  @api.depends('date_ord1_exam_ini')
  def _compute_1term_pfc_exposition_ini(self):
    for record in self:
      if record.date_ord1_exam_ini == False:
        record.date_1term_pfc_exposition_ini = ''
      else: 
        record.date_1term_pfc_exposition_ini = record.date_ord1_exam_ini + datetime.timedelta(weeks = 1)

  @api.constrains('date_1term_pfc_exposition_ini')
  def _check_date_1term_pfc_exposition_ini(self):
    for record in self:
      if record.date_1term_pfc_exposition_ini != False: 
        if record.date_1term_pfc_exposition_ini.weekday() != 0:
          raise ValidationError('La fecha de inicio de las defensas tiene que ser un lunes')
        
  @api.depends('date_2term_pfc_exposition_ini')
  def _compute_2term_pfc_exposition_end(self):
    for record in self:
      if record.date_2term_pfc_exposition_ini == False:
        record.date_2term_pfc_exposition_end = ''
      else: 
        record.date_2term_pfc_exposition_end = record.date_2term_pfc_exposition_ini + datetime.timedelta(days = 4)

  @api.depends('date_1term_pfc_exposition_ini')
  def _compute_1term_pfc_exposition_end(self):
    for record in self:
      if record.date_1term_pfc_exposition_ini == False:
        record.date_1term_pfc_exposition_end = ''
      else: 
        record.date_1term_pfc_exposition_end = record.date_1term_pfc_exposition_ini + datetime.timedelta(days = 4)

  @api.depends('date_2term_pfc_exposition_ini')
  def _compute_2term_pfc_delivery(self):
    for record in self:
      if record.date_2term_pfc_exposition_ini == False:
        record.date_2term_pfc_delivery = ''
      else: 
        record.date_2term_pfc_delivery = record.date_2term_pfc_exposition_ini - datetime.timedelta(days = 10)

  @api.depends('date_1term_pfc_exposition_ini')
  def _compute_1term_pfc_delivery(self):
    for record in self:
      if record.date_1term_pfc_exposition_ini == False:
        record.date_1term_pfc_delivery = ''
      else: 
        record.date_1term_pfc_delivery = record.date_1term_pfc_exposition_ini - datetime.timedelta(days = 10)

  @api.depends('date_1term_pfc_exposition_ini')
  def _compute_1term_pfc_waiver(self):
    for record in self:
      if record.date_1term_pfc_exposition_ini == False:
        record.date_1term_pfc_waiver = ''
      else: 
        record.date_1term_pfc_waiver = record.date_1term_pfc_exposition_ini - datetime.timedelta(days = 30)

  @api.depends('date_2term_pfc_exposition_ini')
  def _compute_2term_pfc_waiver(self):
    for record in self:
      if record.date_2term_pfc_exposition_ini == False:
        record.date_2term_pfc_waiver = ''
      else: 
        record.date_2term_pfc_waiver = record.date_2term_pfc_exposition_ini - datetime.timedelta(days = 30)

  @api.depends('date_2term_pfc_exposition_ini')
  def _compute_2term_pfc_cancellation(self):
    for record in self:
      if record.date_2term_pfc_exposition_ini == False:
        record.date_2term_pfc_cancellation = ''
      else: 
        record.date_2term_pfc_cancellation = record.date_2term_pfc_exposition_ini - datetime.timedelta(days = 60)
   
  @api.depends('date_1term_pfc_exposition_ini')
  def _compute_1term_pfc_cancellation(self):
    for record in self:
      if record.date_1term_pfc_exposition_ini == False:
        record.date_1term_pfc_cancellation = ''
      else: 
        record.date_1term_pfc_cancellation = record.date_1term_pfc_exposition_ini - datetime.timedelta(days = 60)

  @api.depends('date_1term1_end')
  def _compute_1term_pfc_talk(self):
    for record in self:
      if record.date_1term1_end == False:
        record.date_1term_pfc_talk = ''
      else: 
        record.date_1term_pfc_talk = record.date_1term1_end - datetime.timedelta(days = 1)

  @api.depends('date_init')
  def _compute_2term_pfc_talk(self):
    for record in self:
      september_last_day = datetime.date(record.date_init.year, 9, 30)
      # siempre en jueves
      if september_last_day.weekday()>=3:
        record.date_2term_pfc_talk = september_last_day - datetime.timedelta(days = september_last_day.weekday() - 3)
      else:
        record.date_2term_pfc_talk = september_last_day + datetime.timedelta(days = 3 - september_last_day.weekday())

  @api.depends('date_2term_pfc_talk')
  def _compute_2term_pfc_proposal(self):
    for record in self:
      if record.date_2term_pfc_talk == False:
        record.date_2term_pfc_proposal1 = ''
      else: 
        record.date_2term_pfc_proposal1 = record.date_2term_pfc_talk + datetime.timedelta(days = 7)

  @api.depends('date_1term_pfc_talk')
  def _compute_1term_pfc_proposal(self):
    for record in self:
      if record.date_1term_pfc_talk == False:
        record.date_1term_pfc_proposal1 = ''
      else: 
        record.date_1term_pfc_proposal1 = record.date_1term_pfc_talk + datetime.timedelta(days = 14)

  @api.depends('date_2term_pfc_proposal1')
  def _compute_2term_pfc_fixed_proposal(self):
    for record in self:
      if record.date_2term_pfc_proposal1 == False:
        record.date_2term_pfc_proposal2 = ''
      else: 
        record.date_2term_pfc_proposal2 = record.date_2term_pfc_proposal1 + datetime.timedelta(days = 21)

  @api.depends('date_1term_pfc_proposal1')
  def _compute_1term_pfc_fixed_proposal(self):
    for record in self:
      if record.date_1term_pfc_proposal1 == False:
        record.date_1term_pfc_proposal2 = ''
      else: 
        record.date_1term_pfc_proposal2 = record.date_1term_pfc_proposal1 + datetime.timedelta(days = 21)

      
  date_2term_pfc_proposal2= fields.Date(string = 'Entrega propuesta corregidas', compute = '_compute_2term_pfc_fixed_proposal') 

  # ###########
  # FESTIVOS
  # ###########

  @api.onchange('date_init')
  def _calculate_holidays(self):
    for record in self:
      if self._origin.date_init != False:
        # si el año anterior es igual al que se acaba de cambiar no se hace nada
        if self._origin.date_init.year == record.date_init.year:
          continue

      if record.date_init == False:
        continue

      # fiestas de navidad
      date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 23) # de partida es el 23/12
   
      if date_christmas_holidayI.weekday() == 0: # cae lunes
        date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 21)
      elif date_christmas_holidayI.weekday() == 1:  # cae martes
        date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 20)
      elif date_christmas_holidayI.weekday() == 6: # cae domingo
        date_christmas_holidayI = datetime.datetime(record.date_init.year, 12, 22)

      date_christmas_holidayE = datetime.datetime(record.date_init.year + 1, 1, 6) # de partida es el 6/1
      if date_christmas_holidayE.weekday() >= 3 and date_christmas_holidayE.weekday() <= 5:
        date_christmas_holidayE = date_christmas_holidayE + datetime.timedelta(days = 6 - date_christmas_holidayE.weekday())

      # fallas
      date_fallas_holidayI = datetime.datetime(record.date_init.year + 1, 3, 15) # de partida es el 15/3
      if date_fallas_holidayI.weekday() == 0: # cae lunes
        date_fallas_holidayI = datetime.datetime(record.date_init.year, 3, 12)
      elif date_fallas_holidayI.weekday() == 1:  # cae martes
        date_fallas_holidayI = datetime.datetime(record.date_init.year + 1, 3, 20)
      elif date_fallas_holidayI.weekday() == 6: # cae domingo
        date_fallas_holidayI = datetime.datetime(record.date_init.year + 1, 3, 14)

      date_fallas_holidayE = datetime.datetime(record.date_init.year + 1, 3, 19) # de partida es el 19/3
      if date_fallas_holidayE.weekday() >= 3 and date_fallas_holidayE.weekday() <= 5:
        date_fallas_holidayE = date_fallas_holidayE + datetime.timedelta(days = 6 - date_fallas_holidayE.weekday())

      # elimino todos los registros "en el aire", pero se recuperan en el caso de que se cancele la modificación
      # del school_year
      record.holidays_ids = [(5, 0 ,0)]
      # añade nuevos registro, pero los mantiene en "el aire" hasta que se grabe el school_year
      record.holidays_ids = [(0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Día Comunidad Valenciana', 
        'date': datetime.datetime(record.date_init.year, 10, 9), 
        'date_end': datetime.datetime(record.date_init.year, 10, 9) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Día Hispanidad', 
        'date': datetime.datetime(record.date_init.year, 10, 12), 
        'date_end': datetime.datetime(record.date_init.year, 10, 12) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Todos los santos', 
        'date': datetime.datetime(record.date_init.year, 11, 1), 
        'date_end': datetime.datetime(record.date_init.year, 11, 1) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Constitución', 
        'date': datetime.datetime(record.date_init.year, 12, 6), 
        'date_end': datetime.datetime(record.date_init.year, 12, 6),
        'key': 'constitucion' }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Inmaculada', 
        'date': datetime.datetime(record.date_init.year, 12, 8), 
        'date_end': datetime.datetime(record.date_init.year, 12, 8),
        'key': 'inmaculada' }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Navidades', 
        'date': date_christmas_holidayI,
        'date_end': date_christmas_holidayE,
        'key': 'navidad' }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'San Vicente Martir', 
        'date': datetime.datetime(record.date_init.year + 1, 1, 22), 
        'date_end': datetime.datetime(record.date_init.year + 1, 1, 22) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Fallas', 
        'date': date_fallas_holidayI,
        'date_end': date_fallas_holidayE }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': 'Pascuas', 
        'date': self._calc_easter(record.date_init.year + 1) + datetime.timedelta(days = -3),
        'date_end': self._calc_easter(record.date_init.year + 1) + datetime.timedelta(days = 8) }),
        (0, 0, {
        'school_year_id': self._origin.id,
        'description': '1º Mayo', 
        'date': datetime.datetime(record.date_init.year + 1, 5, 1), 
        'date_end': datetime.datetime(record.date_init.year + 1, 5, 1) })
        ]  


  @api.onchange('date_init')
  def _calculate_task(self):
    for record in self:
      if record.date_init == False:
        continue

      courses_id = [x.id for x in self.env['atenea.course'].search([])]
      courses = self.env['atenea.course'].browse(courses_id)  
      cron_ids = []

      record.cron_ids = [(5, 0 ,0)]
      
      for course in courses:
        # descarga desde Aules

        # módulos de tutoria
        _logger.info(course.subjects_ids)
        tut_subjects = [ subject for subject in course.subjects_ids if subject['code'] == '0000']

        _logger.info(tut_subjects)
        if not tut_subjects:
          _logger.error('No hay módulos de tutoria asignados en {}'.format(course.abbr))
          continue

        # únicamente módulos de tutoria que tengan aulas distintas
        distinct_subject_tut = [subject for subject in list(toolz.unique(tut_subjects, key=lambda x: x.classroom_id))]
    
        for subject in distinct_subject_tut:   

          ## MATRICULA 
          task = (0, 0, {
            'model_id': record.env.ref('atenea.model_atenea_classroom'),
            'name': 'Matricula alumnos de {} en Atenea {}'.format(course.abbr, 
              '/{}'.format(subject.year) if len(list(distinct_subject_tut)) > 1 else ''),
            'active': True,
            'interval_number': 1,
            'interval_type': 'days',
            'numbercall': 60,     # número de veces que será ejecutada la tarea
            'doall': 1,           # si el servidor cae, cuado se reinicie lanzar las tareas no ejecutadas
            'nextcall': '2023-03-02 00:27:59',
            'state': 'code',
            'code': 'model.cron_enrol_students({}, {}, {})'
              .format(subject.classroom_id.moodle_id,
                subject.id,
                course.id,
                subject.id),
          }) 
      
          cron_ids.append(task)

          ## CONVALIDACIONES     
          task = (0, 0, {
            'model_id': record.env.ref('atenea.model_atenea_classroom'),
            'name': 'Descarga datos convalidaciones {} desde Aules {}'.format(course.abbr, 
              '/{}'.format(subject.year) if len(list(distinct_subject_tut)) > 1 else ''),
            'active': True,
            'interval_number': 1,
            'interval_type': 'days',
            'numbercall': 60,     # número de veces que será ejecutada la tarea
            'doall': 1,           # si el servidor cae, cuado se reinicie lanzar las tareas no ejecutadas
            'nextcall': '2023-03-02 00:27:59',
            'state': 'code',
            'code': 'model.cron_download_validations({}, {}, {}, {})'
              .format(subject.classroom_id.moodle_id,
                subject.id,
                subject.classroom_id.get_task_id_by_key('validation'),
                course.id),
            #'code': 'model._cron_download_validations({},{},"{}")'
            #  .format(2094,183989,course.abbr),
          }) 
      
          cron_ids.append(task)
 

      _logger.info(cron_ids)
    
      # añade nuevos registro, pero los mantiene en "el aire" hasta que se grabe el school_year 
      record.cron_ids = cron_ids
     
  

  """
  https://www.daniweb.com/programming/software-development/code/463551/another-look-at-easter-dates-python
  """
  @staticmethod
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

    self.dates['date_welcome_day'] = { 
      'date': self.date_welcome_day, 
      'desc': self._fields['date_welcome_day'].string,
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
    
    self.dates['date_2term2_ini'] = { 
      'date': self.date_2term2_ini,
      'desc': self._fields['date_2term2_ini'].string, 
      'type': 'S',
    }

    self.dates['date_2term2_end'] = { 
      'date': self.date_2term2_end,
      'desc': self._fields['date_2term2_end'].string, 
      'type': 'S',
    }

    self.dates['date_2term2_exam_ini'] = { 
      'date': self.date_2term2_exam_ini,
      'desc': self._fields['date_2term2_exam_ini'].string, 
      'type': 'S',
      'dur': self.date_2term2_exam_end - self.date_2term2_exam_ini
    }

    self.dates['date_2term2_exam_end'] = { 
      'date': self.date_2term2_exam_end,
      'desc': self._fields['date_2term2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_2term2_exam_ini - self.date_2term2_exam_end,
    }

    self.dates['date_ord2_exam_ini'] = { 
      'date': self.date_ord2_exam_ini,
      'desc': self._fields['date_ord2_exam_ini'].string, 
      'type': 'S',
      'dur': self.date_ord2_exam_end - self.date_ord2_exam_ini,
    }

    self.dates['date_ord2_exam_end'] = { 
      'date': self.date_ord2_exam_end,
      'desc': self._fields['date_ord2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_ord2_exam_ini - self.date_ord2_exam_end,
    }

    self.dates['date_extraord2_exam_ini'] = { 
      'date': self.date_extraord2_exam_ini,
      'desc': self._fields['date_extraord2_exam_ini'].string, 
      'type': 'S',
      'dur': self.date_extraord2_exam_end - self.date_extraord2_exam_ini,
    }

    self.dates['date_extraord2_exam_end'] = { 
      'date': self.date_extraord2_exam_end,
      'desc': self._fields['date_extraord2_exam_end'].string, 
      'type': 'S',
      'dur': self.date_extraord2_exam_ini - self.date_extraord2_exam_end,
    }
    
    self.dates['date_cancellation2'] = { 
      'date': self.date_cancellation2,
      'desc': self._fields['date_cancellation2'].string, 
      'type': 'S',
    }
  
    self.dates['date_waiver_ord2'] = { 
      'date': self.date_waiver_ord2,
      'desc': self._fields['date_waiver_ord2'].string, 
      'type': 'S',
    }
  
    self.dates['date_waiver_extraord2'] = { 
      'date': self.date_waiver_extraord2,
      'desc': self._fields['date_waiver_extraord2'].string, 
      'type': 'S',
    }

    self.dates['1term1_end'] = { 
      'date': self.date_1term1_end,
      'desc': self._fields['date_1term1_end'].string, 
      'type': 'P'
    }

    self.dates['date_1term1_exam_ini'] = { 
      'date': self.date_1term1_exam_ini,
      'desc': self._fields['date_1term1_exam_ini'].string, 
      'type': 'P',
      # días que dura este evento, además del día indicado
      'dur': self.date_1term1_exam_end - self.date_1term1_exam_ini
    }

    self.dates['date_1term1_exam_end'] = { 
      'date': self.date_1term1_exam_end,
      'desc': self._fields['date_1term1_exam_end'].string, 
      'type': 'P',
      'dur': self.date_1term1_exam_ini - self.date_1term1_exam_end,
    }
    
    self.dates['date_2term1_ini'] = { 
      'date': self.date_2term1_ini,
      'desc': self._fields['date_2term1_ini'].string, 
      'type': 'P',
    }

    self.dates['date_2term1_end'] = { 
      'date': self.date_2term1_end,
      'desc': self._fields['date_2term1_end'].string, 
      'type': 'P',
    }

    self.dates['date_2term1_exam_ini'] = { 
      'date': self.date_2term1_exam_ini,
      'desc': self._fields['date_2term1_exam_ini'].string, 
      'type': 'P',
      'dur': self.date_2term1_exam_end - self.date_2term1_exam_ini
    }

    self.dates['date_2term1_exam_end'] = { 
      'date': self.date_2term1_exam_end,
      'desc': self._fields['date_2term1_exam_end'].string, 
      'type': 'P',
      'dur': self.date_2term1_exam_ini - self.date_2term1_exam_end,
    }
    
    self.dates['date_ord1_exam_ini'] = { 
      'date': self.date_ord1_exam_ini,
      'desc': self._fields['date_ord1_exam_ini'].string, 
      'type': 'P',
      'dur': self.date_ord1_exam_end - self.date_ord1_exam_ini,
    }

    self.dates['date_ord1_exam_end'] = { 
      'date': self.date_ord1_exam_end,
      'desc': self._fields['date_ord1_exam_end'].string, 
      'type': 'P',
      'dur': self.date_ord1_exam_ini - self.date_ord1_exam_end,
    }

    self.dates['date_extraord1_exam_ini'] = { 
      'date': self.date_extraord1_exam_ini,
      'desc': self._fields['date_extraord1_exam_ini'].string, 
      'type': 'P',
      'dur': self.date_extraord1_exam_end - self.date_extraord1_exam_ini,
    }

    self.dates['date_extraord1_exam_end'] = { 
      'date': self.date_extraord1_exam_end,
      'desc': self._fields['date_extraord1_exam_end'].string, 
      'type': 'P',
      'dur': self.date_extraord1_exam_ini - self.date_extraord1_exam_end,
    } 
    
    self.dates['date_cancellation1'] = { 
      'date': self.date_cancellation1,
      'desc': self._fields['date_cancellation1'].string, 
      'type': 'P',
    }
  
    self.dates['date_waiver_ord1'] = { 
      'date': self.date_waiver_ord1,
      'desc': self._fields['date_waiver_ord1'].string, 
      'type': 'P',
    }
     
    self.dates['date_waiver_extraord1'] = { 
      'date': self.date_waiver_extraord1,
      'desc': self._fields['date_waiver_extraord1'].string, 
      'type': 'P',
    }
