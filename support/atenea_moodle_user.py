# -*- coding: utf-8 -*-
from moodleteacher.users import MoodleUser
from moodleteacher.requests import MoodleRequest

import logging

_logger = logging.getLogger(__name__)

class AteneaMoodleUser(MoodleUser):
  """
  Amplia los datos que se obtienen de un usuario

  Hereda de MoodleUser
  """
  
  # nuevos atributos
  username = None
  lastname = None
  firstname = None

  @classmethod
  def from_userid(cls, conn, user_id):
    obj = cls()
    obj.id_ = user_id
    params = {'field': 'id', 'values[0]': str(user_id)}
    response = MoodleRequest(
      conn, 'core_user_get_users_by_field').post(params).json()
    if response != []:
      assert(response[0]['id'] == user_id)

      _logger.info(response)

      obj.fullname = response[0]['fullname']
      obj.email = response[0]['email']
      #obj.username = response[0]['username']
      obj.lastname = response[0]['lastname']
      obj.firstname = response[0]['firstname']
    else:
      obj.fullname = "<Unknown>"
      obj.email = "<Unknown>"
      #obj.username = "<Unknown>"
      obj.lastname = "<Unknown>"
      obj.firstname = "<Unknown>"
   
    return obj
    
   

   