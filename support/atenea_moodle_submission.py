# -*- coding: utf-8 -*-
from moodleteacher.submissions import MoodleSubmission
from ..support.atenea_moodle_submission import MoodleSubmission
from moodleteacher.requests import MoodleRequest

import logging

_logger = logging.getLogger(__name__)

class AteneaMoodleSubmission(MoodleSubmission):
  """
  Amplia la fucionalidad de MoodleSubmission

  Hereda de MoodleSubmission
  """

  # al no definir el init toma el del padre

  def set_user_flags(self, user_flags):
    """
    Asigna características de la tarea enfocada a un determinado usuario.
    Caracerísticas como locked, extensionduedate
    https://github.com/moodle/moodle/blob/df502b3e4c86f9d2d5fbe8baa7ab9d5aa9d45fe8/mod/assign/externallib.php#L958

    Ejemplo user_flags {
      'assignmentid': self.assignment.id_,   # obligatorio
      'userflags[0][userid]': userid,        # obligatorio
      'locked': int(True)                    # opcional 
    }
    """
    
    response = MoodleRequest(
      self.conn, 'mod_assign_set_user_flags').post(data = user_flags).json()
    
  def lock(self):
    if self.is_group_submission():
      userid = self.get_group_members()[0].id_
    else:
      userid = self.userid

    self.set_user_flags({
      'assignmentid': self.assignment.id_,
      'userflags[0][userid]': userid,
      'userflags[0][locked]': int(True),
    })

  def unlock(self):
    if self.is_group_submission():
      userid = self.get_group_members()[0].id_
    else:
      userid = self.userid

    self.set_user_flags({
      'assignmentid': self.assignment.id_,
      'userflags[0][userid]': userid,
      'userflags[0][locked]': int(False),
    })

