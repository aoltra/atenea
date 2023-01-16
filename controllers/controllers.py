# -*- coding: utf-8 -*-
# from odoo import http


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
