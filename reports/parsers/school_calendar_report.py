from odoo import models
import logging
import datetime
import calendar
import copy

_logger = logging.getLogger(__name__)

""" parser para procesar la plantilla del calendario escolar
Antes de buscar los valores en los datos del modelo asociado (en este caso school_year)
el motor de informes busca si hay algun modelo que conicida con el nombre del report
(report + atributo name del elemento report) """
class SchoolCalendarReport(models.AbstractModel):
  _name = 'report.atenea.report_school_calendar'
  _description = 'Parser report calendario escolar'

  def _include_dates_month(self, month_cal, dt):
    prev = month_cal[:month_cal[:month_cal.find('>' + str(dt['date'].day) + '<')].rindex("class") + 7]
    end = month_cal[month_cal[:month_cal.find('>' + str(dt['date'].day) + '<')].rindex("class") + 7:]

    return prev +  dt['type'] + '-type ' + end
  
  """ Devuelve una tabla HTML (sólo tr) con las fechas del mes"""
  def _generate_li_dates(self, date_month):
    date_month.sort(key = lambda x: x['date'].day)

    range_day =  []

    table_tr = ''
    for dt in date_month:
      if 'dur' in dt:
        if dt['date'] < dt['date'] + dt['dur']:
          day = '%s-%s' % (dt['date'].day, str((dt['date'] + dt['dur']).day))
        else:
          day = '%s-%s' % (str((dt['date'] + dt['dur']).day), dt['date'].day)

        # para que no aparezca la fecha dos veces en el mismo mes, por el inicio y fin de rango
        if day not in range_day:
          range_day.append(day)
        else:
          continue

        description = dt['desc'].partition(' ')[2].lower()
      else:
        day = str(dt['date'].day)
        description = dt['desc'].lower()

      table_tr += '<tr><td>' + day + '</td><td>:</td><td>' + description + '</td></tr>'
    
    return table_tr

  def _get_report_values(self, docids, data=None):
    _logger.info("Parser generación calendario escolar")

    months = [ 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    html_cal = calendar.HTMLCalendar(firstweekday = 0)

    months_calendar = {}

    docs = self.env['atenea.school_year'].browse(docids)

    for doc in docs:
      doc.update_dates()   # se actualiza la estructura de fechas
      months_calendar[doc.id] = []
      
      for month in months:
        month_cal = html_cal.formatmonth(doc.date_init.year + 1  if month <7 else doc.date_init.year, month)

        # fechas de school_year.dates que son del mes month
        # enumerate convierte una lista en un diccionario con key indices: 0,1,2,3...
        date_month = [x for i,x in enumerate(doc.dates.values()) if x['date'].month == month]
      
        for dt in date_month:
          month_cal = self._include_dates_month(month_cal, dt)
          if 'dur' in dt:
            dtT = copy.deepcopy(dt)
            days = range(dt['dur'].days) if dt['dur'].days > 0 else range(dt['dur'].days, 0)
            for day in days:
              dtT['date'] = dt['date'] + datetime.timedelta(days = day + 1)
              month_cal = self._include_dates_month(month_cal, dtT)
   
        month_cal +='<table class="description">' + self._generate_li_dates(date_month)  + ' </table>' 
        months_calendar[doc.id].append(month_cal)


    # se devuelve lo que interese que aparezca en el template
    return {
      'doc_ids': docids,                                      # obligatorio
      'doc_model': 'atenea.school_year',                      # obligatorio
      'docs': docs,                                           # obligatorio
      'months_cal': months_calendar
    }