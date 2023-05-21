# -*- coding: utf-8 -*-
from moodleteacher.submissions import MoodleSubmission
from .atenea_moodle_submission import MoodleSubmission
#from moodleteacher.requests import MoodleRequest
from .atenea_moodle_request import AteneaMoodleRequest

import logging

_logger = logging.getLogger(__name__)

GRADED = 'graded'
NOT_GRADED = 'notgraded'
NEW = 'new'
SUBMITTED = 'submitted'

class AteneaMoodleSubmission(MoodleSubmission):
  """
  Amplia la fucionalidad de MoodleSubmission

  Hereda de MoodleSubmission
  """

  def __init__(self, conn=None, submission_id=None, assignment=None, 
               user_id=None, group_id=None, status=None, gradingstatus=None, 
               textfield=None, files=[], attemptnumber = 0):
        self.attemptnumber = attemptnumber
        super().__init__(conn, submission_id, assignment, 
               user_id, group_id, status, gradingstatus, 
               textfield, files)

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
    
    response = AteneaMoodleRequest(
      self.conn, 'mod_assign_set_user_flags').post(data = user_flags).json()
    
  def get_user_id(self):
    if self.is_group_submission():
      userid = self.get_group_members()[0].id_
    else:
      userid = self.userid

    return userid
    
  def lock(self):
    self.set_user_flags({
      'assignmentid': self.assignment.id_,
      'userflags[0][userid]': self.get_user_id(),
      'userflags[0][locked]': int(True),
    })

  def unlock(self):
    self.set_user_flags({
      'assignmentid': self.assignment.id_,
      'userflags[0][userid]': self.get_user_id(),
      'userflags[0][locked]': int(False),
    })

  def set_extension_due_date(self, to):   
    self.set_user_flags({
      'assignmentid': self.assignment.id_,
      'userflags[0][userid]': self.get_user_id(),
      'userflags[0][extensionduedate]': to,
    })

  def save_grade(self, grade, new_attempt = False, feedback = None):
    """
    Graba una nueva nota para un estudiante y pasa su estado a GRADED
  
    Permite indicar si se desea permitir otro intento
    """
    # You can only give text feedback if your assignment is configured accordingly
    if feedback is not None and not self.assignment.allows_feedback_comment:
      _logger.error("Could not save feedback, assignment does not allow feedback comments. Please check your assignment settings in Moodle.")
      return

    if self.is_group_submission():
      userid = self.get_group_members()[0].id_
    else:
      userid = self.userid

    data = {
      'assignmentid': self.assignment.id_,
      'userid': userid,
      'workflowstate': GRADED,
      'attemptnumber': -1,
      'addattempt': int(new_attempt),
      'grade': float(grade) if grade else '',
      # always apply grading to team
      # if the assignment has no group submission, this has no effect.
      'applytoall': int(True),
      'plugindata[assignfeedbackcomments_editor][text]': str(feedback) if feedback else "",
      # //content format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN)
      'plugindata[assignfeedbackcomments_editor][format]': 1
    }

    response = AteneaMoodleRequest(
      self.conn, 'mod_assign_save_grade').post(data = data).json()
    _logger.debug("Response from grading update: {0}".format(response))

