# -*- coding: utf-8 -*-
import collections
from moodleteacher.requests import MoodleRequest
from ..atenea_logger.exceptions import AteneaException

import requests

import logging

_logger = logging.getLogger(__name__)

class AteneaBaseRequest():
  """
  A HTTP(S) request that considers :class:`MoodleConnection` settings.
  """

  def __init__(self, conn, url, attempts = 0):
    """
    attempts: número de intentos antes de generar una excepción de error de conexión, 0 = infinitos
    """
    self.conn = conn
    self.url = url
    self.attempts = attempts
    
  def get_absolute(self, params=None):
    if self.conn.is_fake:
      _logger.info("Fake connection no supported")

    _logger.debug("Performing web service GET call ...")
    nattempt = 0
    while (nattempt < self.attempts or self.attempts == 0):
      nattempt += 1
      try:
        result = requests.get(self.url, params=params, timeout=self.conn.timeout)
      except requests.exceptions.Timeout:
        _logger.error("Timeout for GET request to {0} after {1} seconds, trying again.".format(self.url, self.conn.timeout))
        continue
      break

    if nattempt == self.attempts:
      raise Exception('Max. number of connection ({0}) attempts reached'.format(self.attempts))
      
    _logger.debug("Result status code: {0}".format(result.status_code))
    result.raise_for_status()
    return result

  def post_absolute(self, params=None, data=None):
    if self.conn.is_fake:
      _logger.info("Fake connection no supported")
    
    _logger.debug("Performing web service POST call ...")
    nattempt = 0
    while (nattempt < self.attempts or self.attempts == 0):
      nattempt += 1
      try:
        result = requests.post(self.url, params=params, data=data, timeout=self.conn.timeout)
      except requests.exceptions.Timeout:
        _logger.error("Timeout for POST request to {0} after {1} seconds, trying again.".format(self.url, self.conn.timeout))
        continue
      break

    if nattempt == self.attempts:
      raise Exception('Max. number of connection ({0}) attempts reached'.format(self.attempts))
      
    _logger.debug("Result status code: {0}".format(result.status_code))
    result.raise_for_status()
    return result


class AteneaMoodleRequest(AteneaBaseRequest):
  """
  Caza excepciones MoodleRequest y las relanza via AteneaExcepction
  Permite limitar el número de intentos de conexión
  
  Esta clase es prácticamente la misma que la orginal, salvo el control de excepciones y que hereda
  de AteneaBaseRequest. La forma más sencilla sería modificar la clase BaseRequest de moodleTeacher para
  incluir el número de intentos y posteriormente heredar MoodleRequest para hacer el control de excepciones.
  Se ha solicitado creado un issue https://github.com/troeger/moodleteacher/issues/10
  """

  def __init__(self, conn, funcname, attempts=6):
    """
    Prepares a Moodle web service API request that considers :class:`MoodleConnection` settings.

    Parameters:
        conn: The MoodleConnection object.
        funcname: The name of the Moodle web service function.
        attempts: number of connection attempts
    """
    
    super().__init__(conn, conn.ws_url, attempts)
    self.base_params = {'wsfunction': funcname,
                        'moodlewsrestformat': 'json',
                        'wstoken': conn.token}

  def _encode_param(self, params, key, value):
    """
    Convert Python sequences to numbered JSON list,
    and Python numbers to strings.
    """
    if isinstance(value, collections.Sequence) and not isinstance(value, str):
        for i, v in enumerate(value):
            self._encode_param(params, "{}[{}]".format(key, i), v)
        return
    if isinstance(value, int):
        value = str(value)
    params[key] = value

  def get(self, params=None):
    """
    Perform a GET request to the Moodle web service API.
    """
    real_params = self.base_params.copy()
    # Convert addtional parameters into correct format
    # Base parameters are already fine
    if params:
        for k, v in params.items():
            self._encode_param(real_params, k, v)
    try:
      result = self.get_absolute(params=real_params)
    except Exception as e:
      raise AteneaException(
        _logger, 
        str(e),
        50, # critical
        comments = '''Tal vez el servicio Moodle no esté arrancado o haya caído''')
    
    data = result.json()
    # logger.debug("Result: {0}".format(data))           # massive data amount, also security sensitive
    _logger.debug("Result: {0}".format(result))
    if isinstance(data, dict) and "exception" in data:
      raise Exception(
          "Error response for Moodle web service GET request ('{message}')".format(**result.json()))
    return result

  def post(self, params=None, data=None):
      """
      Perform a POST request to the Moodle web service API.
      """
      # Convert addtional parameters into correct format
      # Base parameters are already fine
      real_params = self.base_params.copy()
      if params:
          for k, v in params.items():
              self._encode_param(real_params, k, v)
      try:
        result = self.post_absolute(params=real_params, data=data)
      except Exception as e:      
        raise AteneaException(
          _logger, 
          str(e),
          50, # critical
          comments = '''Tal vez el servicio Moodle no esté arrancado o haya caído''')
      
      data = result.json()
      # logger.debug("Result: {0}".format(data))          # massive data amount, also security sensitive
      _logger.debug("Result: {0}".format(result))
      if isinstance(data, dict):
          if "exception" in data:
              raise Exception(
                  "Error response for Moodle web service POST request ('{message}')".format(**result.json()))
      return result