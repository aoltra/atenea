# -*- coding: utf-8 -*-

from moodleteacher.courses import MoodleCourse
from moodleteacher.requests import MoodleRequest
from moodleteacher.assignments import MoodleAssignment
from .atenea_moodle_submission import AteneaMoodleSubmission

import logging
logger = logging.getLogger('moodleteacher')

class AteneaMoodleAssignment(MoodleAssignment):
  """
  Amplia la fucionalidad de MoodleAssignment

  Hereda de MoodleAssignment

  NOTA: Por alguna razón desconocida, el id de la tarea que aparece en la barra de navegación del 
        navegador no es del id que devuelve la API (el de la API es id-1). 
        Aun asi el funcionamiento es correcto
  """

  # al no definir el init toma el del padre

  def get_user_submission(self, user_id, must_have_files=True):
    """
    Create a new :class:`AteneaMoodleSubmission` object with the submission of
    the given user in this assignment, or None.
    When must_have_files is set to True, only submissions with files are considered.
    """
    params = {}
    params['assignid'] = self.id_
    params['userid'] = user_id
    logger.info("Fetching submission information for user {userid} in assignment {assignid}".format(**params))
    try:
      response = MoodleRequest(
        self.conn, 'mod_assign_get_submission_status').get(params).json()
    except Exception as e:
      logger.error("Could not fetch submission information:")
      logger.exception(e)
      return None
    
    if 'lastattempt' in response:
      if 'submission' in response['lastattempt']:
        if must_have_files:
          plugin_list = response['lastattempt']['submission']['plugins']
          for plugin_data in plugin_list:
            if plugin_data['type'] == 'file' and len(plugin_data['fileareas'][0]['files']) == 0:
              # Submission with no files
              # We had that effect of ghost submissions, were people never
              # even watched the assignment and still got submissions registered
              # This is the safeguard to protect from that
              logger.error('Submission with empty file list, ignoring it.')
              return None

        submission = AteneaMoodleSubmission(
          conn=self.conn,
          submission_id=response['lastattempt']['submission']['id'],
          assignment=self,
          user_id=response['lastattempt']['submission']['userid'],
          status=response['lastattempt']['submission']['status'])
        if 'teamsubmission' in response['lastattempt']:
          logger.debug("Identified team submission.")
          submission.group_id = response['lastattempt']['teamsubmission']['groupid']
          submission.parse_plugin_json(response['lastattempt']['teamsubmission']['plugins'])
        else:
          logger.debug("Identified single submission.")
          submission.parse_plugin_json(response['lastattempt']['submission']['plugins'])
        return submission
      
    return None
 
  def set_extension_due_date(self, users):
    """
    Modifica la fecha de entrega de una tarea (assignment) por usuario, sin que haga falta 
    que el usuario haya entregado algo (submission)
    """

    params = {'assignmentid': self.id_}
    num_user = 0

    for u,d in users:
      params['userids['+ str(num_user) + ']'] = u
      params['dates['+ str(num_user) + ']'] = d
      num_user += 1 

    if len(users) > 0:
      try:
        response = MoodleRequest(
          self.conn, 'mod_assign_save_user_extensions').post(params).json()
      except Exception as e:
        logger.error("Error en [set_extension_due_date]: " + str(e))
  

class AteneaMoodleAssignments(list):
  """
  Una lista de instancias de la :class:`AteneaMoodleAssignment`.

  Hereda de MoodleAssignments
  """

  def __init__(self, conn, course_filter=None, assignment_filter=None):
    params = {}
    if course_filter:
      params['courseids'] = course_filter
      response = MoodleRequest(
          conn, 'mod_assign_get_assignments').get(params).json()
      if 'courses' in response:
        for course_data in response['courses']:
          course = MoodleCourse.from_raw_json(conn, course_data)
          if (course_filter and course.id_ in course_filter) or not course_filter:
            for ass_data in course_data['assignments']:
              assignment = AteneaMoodleAssignment.from_raw_json(
                  course, ass_data)
              if (assignment_filter and assignment.cmid in assignment_filter) or not assignment_filter:
                  self.append(assignment)