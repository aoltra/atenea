# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import time

class OdooLogHandler(logging.Handler):
  """
  Crea un manejador para que los registro del log
  puedan almacenarse en una tabla de Odoo 
  """
  def __init__(self, path_log):
    logging.Handler.__init__(self)
    self.path_log = path_log
  
  def emit(self, record):
    log_msg = record.msg
    log_msg = log_msg.strip()
    tm = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(record.created))

    now = datetime.now()
    number_reports_per_day = 3  # TODO: comfigurar en settings???

    for inter in range(int(24 / number_reports_per_day), 25, int(24 / number_reports_per_day)):
      if now.hour < inter:
        range_hours = '{:02d}:00-{:02d}:59'.format(inter - int(24 / number_reports_per_day),
          inter - 1)
        break
      
    filename = self.path_log \
      + '/odoo_{:04d}{:02d}{:02d}_{}.log'.format(now.year, now.month, now.day, range_hours)
    
    filename = filename.replace('//', '/')

    with open(filename, 'a') as f:
      f.write('{} - [{:02d}:{}] {}\n'.format(tm, record.levelno, record.level_name, record.name))
      f.write('{} {}\n'.format(' '*21, log_msg))
      f.write('\n')
      f.write('{} {}\n'.format(' '*21, record.comments))
      f.write('\n')
      f.write('-'*88)
      f.write('\n')
    