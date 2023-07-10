# -*- coding: utf-8 -*-
from email.policy import default
from odoo import http
from odoo.http import request

class ValidationController(http.Controller):

  @http.route('/validation/validation_banner/', auth='user', type='json')
  def get_banner_data(self, **kw):
    """
    Ruta para mostar en banner en las convalidaciones
    No se permite la llamada directa desde el navegador ya que el tipo es json, np http
    """
    user =  request.env.user
    is_coord = is_validator= is_root = is_admin = False
     
    if user.has_group('atenea.group_VALID'):
      is_validator = True

    if user.has_group('atenea.group_ADMIN'):
      is_admin = True

    if user.has_group('atenea.group_MNGT_FP'):
      is_coord = True
    
    if user.has_group('atenea.group_ROOT'):
      is_root = True

    courses = [rol.course_id.abbr for rol in user.employee_id.roles_ids if rol.course_id.abbr is not False]

    if len(courses)>0:
      user_num_valid = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses)])
      user_num_resolved = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses),
                                                                               ('state','=','3')])
      user_num_for_correction = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses),
                                                                                     ('state','=','1')])  
      user_num_higher_level = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses),
                                                                                     ('state','=','2')])
      user_in_process = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses),
                                                                                     ('state','=','0')])  
    else:
      user_num_valid = user_num_resolved = user_num_for_correction = user_num_higher_level = user_in_process = 0

    num_valid = request.env['atenea.validation_subject'].search_count([])
    num_resolved = request.env['atenea.validation_subject'].search_count([('state','=','3')])
    num_reviewed = request.env['atenea.validation_subject'].search_count([('state','=','4')])
    num_higher_level = request.env['atenea.validation_subject'].search_count([('state','=','2')])
    # el dominio se define mediante notación polaca
    num_finished = request.env['atenea.validation_subject'].search_count(['|', ('state','=','6'), ('state','=','7')])
    num_rejected = request.env['atenea.validation_subject'].search_count(['&', ('state','=','3'), ('accepted','=','2')])


    return {
      # hay que prefijar con el nombre del módulo, aunque el id del template no lo lleva
      'html': request.env.ref('atenea.validation_banner_template')._render({
              'is_root': is_root,
              'num_valid': num_valid,
              # es validador
              'is_validator': is_validator,
              'user_num_valid': user_num_valid,
              'user_num_resolved': user_num_resolved,
              'user_num_for_correction': user_num_for_correction,
              'user_num_higher_level': user_num_higher_level,
              'user_in_process': user_in_process,
              # es revisor
              'is_coord': is_coord,
              'num_resolved': num_resolved,
              'num_reviewed_in_process': num_resolved - num_reviewed,
              # es secretaría
              'is_admin': is_admin,
              'num_finished': num_finished,
              'num_reviewed': num_reviewed,
              'num_finished_in_process': num_reviewed - num_finished,
              'num_higher_level': num_higher_level,
              'num_rejected': num_rejected 
            })
          } 


  """   return {


          </div>
          <div class="col col-sm col-md-7">
            <div class="alert alert-warning fade show" role="alert"><i class="bi bi-envelope-exclamation-fill"></i>Hay 3 nuevas convalidaciones pendientes
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div id="correction-alert" class="alert alert-danger" role="alert">Hay 2 nuevas subsanciones enviadas</div>
            <div class="alert alert-warning" role="alert">Hay 2 nuevas resoluciones enviadas</div>
            <div class="alert alert-warning" role="alert">Hay 6 nuevas convalidaciones por finalizar</div>
            <div class="alert alert-info" role="alert">Están pendientes 2 instancias superiores</div>
          </div>
        </div>  
      </div>
    
    }
     return http.request.env['ir.ui.view'].render_template(
        'atenea.validation_banner_template',
        {'user': http.request.env.user}
    )     
    , {
             'root': '/atenea/atenea',
             'object': http.request.env['atenea.validation'],
         }) 
  """    
