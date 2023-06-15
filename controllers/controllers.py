# -*- coding: utf-8 -*-
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

    courses = [rol.course_id.abbr for rol in user.employee_id.roles_ids]
    user_num_valid = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses)])
    user_num_resolved = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses),
                                                                               ('state','=','3')])
    user_num_for_correction = request.env['atenea.validation_subject'].search_count([('validation_id.course_id.abbr', 'in', courses),
                                                                                     ('state','=','1')])  


    return {
      # hay que prefijar con el nombre del módulo, aunque el id del template no lo lleva
      'html': request.env.ref('atenea.validation_banner_template')._render({
              'is_root': is_root,
              # es validador
              'is_validator': is_validator,
              'user_num_valid': user_num_valid,
              'user_num_resolved': user_num_resolved,
              'user_num_for_correction': user_num_for_correction,
              'user_num_higher_level': 0,
              # es revisor
              'is_coord': is_coord,
              'num_correction': 0,
              # es secretaría
              'is_admin': is_admin,
              'num_ended': 0,
              'num_higher_level': 0,
              'num_valid': 0,
            })
          } 





  """   return {
      'html': "
      <div class="container-fluid" style="padding-top: 0.8rem; padding-bottom: 0.8rem">
        <div class="row">
          <div class="col col-sm col-md-5">
            <div class="row"> <!-- estadística convalidador -->
              <div class="col col-sm">
                <span class="bg-success" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">Resueltas</span>
                <span class="bg-warning" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">En proceso</span>
                <span class="bg-danger" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">Subsanación</span>
                <span class="bg-info" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">Instancia superior</span>
              </div>
            </div>
            <div class="row">
              <div class="col col-sm">
                <div class="progress">
                  <div class="progress-bar bg-success" role ="progressbar" style="width: 35%;">35%</div>
                  <div class="progress-bar bg-warning" style="width: 20%;">20%</div>
                  <div class="progress-bar bg-info" style="width: 10%;"></div>  <!-- instancia superior -->
                  <div class="progress-bar bg-danger" style="width: 10%;"></div>
                </div>
              </div>
            </div>

            <div class="row"> <!-- estadística revisor -->
              <div class="col col-sm">
                <span class="bg-success" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">Resueltas</span>
                <span class="bg-warning" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">En proceso</span>
                <span class="bg-danger" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">Subsanación</span>
                <span class="bg-info" style="display: inline-block; width: 10px; height: 10px; border-radius: 5px; background-color: red"></span>
                <span style="margin-right: 1rem">Instancia superior</span>
              </div>
            </div>
            <div class="row">
              <div class="col col-sm">
                <div class="progress">
                  <div class="progress-bar bg-success" role ="progressbar" style="width: 35%;">35%</div>
                  <div class="progress-bar bg-warning" style="width: 20%;">20%</div>
                  <div class="progress-bar bg-info" style="width: 10%;"></div>  <!-- instancia superior -->
                  <div class="progress-bar bg-danger" style="width: 10%;"></div>
                </div>
              </div>
            </div>


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

# class Atenea(http.Controller):
#     @http.route('/atenea/atenea/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/atenea/atenea/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('atenea.listing', {
#             'root': '/atenea/atenea',
#             'objects': http.request.env['atenea.atenea'].search([]),
#         })

#     @http.route('/atenea/atenea/objects/<model("atenea.atenea"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('atenea.object', {
#             'object': obj
#         })
