# -*- coding: utf-8 -*-
import os
import pickle
import json
from moodleteacher.connection import MoodleConnection  

import logging

_logger = logging.getLogger(__name__)

class AteneaMoodleConnection(MoodleConnection):
  """
    Configura una conexión a un ser servidor de Moodle a partir
    de los datos almacenados enn ~/.atenea_moodleteacher.

    Hereda de MoodleConnection 
    
    Args:
      moodle_host:        La URL base del servidor de Moodle
      user:               Usuario Moodle que realiza la conexión
  """
  def __init__(self, moodle_user, moodle_host):

    if not moodle_host or not moodle_user:
      raise AttributeError('No se ha proporcionado usuario o url.')
      return
    
    try:
      with open(os.path.expanduser("~/.atenea_moodleteacher"), "rb") as f:
        users_tokens = pickle.load(f)
    except Exception:
      _logger.error('No se encuentra el fichero .atena_moodleteacher. Utiliza el script save_token_moodle para generarlo.')
      return
  
    if moodle_user not in users_tokens:
      _logger.error('El usuario {} no se encuentra en el fichero .atena_moodleteacher. Utiliza el script save_token_moodle para añadirlo.'.format(user))


    super().__init__(moodle_host,  users_tokens[moodle_user])
    