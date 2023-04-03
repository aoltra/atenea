# -*- coding: utf-8 -*-

from .odoo_handler import OdooLogHandler

odoo_handler = OdooLogHandler('/var/log/odoo')

class AteneaException(Exception):
  """
  Excepción lanzada para errores de Atenea
  Permite la grabación de la excepción en el log y en la base de datos de Atenea

  https://docs.python.org/3/library/logging.html#logging-levels
  """
  LOG_LEVELS = {
    50: 'CRITICAL',
    40: 'ERROR',
    30: 'WARNING',
    20: 'INFO',
    10: 'DEBUG',
     0: 'NOTSET'
  }

  def __init__(self, logger, msg = '', level = 40, level_name = '', comments = '', stack = False, toFile = False):
    """
    stack: muestra la pila o no
    toFile: además, envia la información al fichero de LOG
    """
    self.msg = msg
    self.level = level
    self.level_name = level_name
    self.comments = comments
    self.stack = stack

    if level >= 40:
      toFile = True

    if len(self.level_name) == 0:
      self.level_name = AteneaException.LOG_LEVELS[level]

    if toFile:
      logger.addHandler(odoo_handler)

    extra_data = { 'comments': self.comments, 'level_name': self.level_name } 
    logger.log(level, msg, stack_info = self.stack, extra = extra_data) 
      
    if toFile:
      logger.removeHandler(odoo_handler)

  def __str__(self):
    return self.msg