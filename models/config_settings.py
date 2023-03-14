# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    moodle_user = fields.Char(string = 'Usuario acceso a Moodle', config_parameter='atenea.moodle_user')
    moodle_url = fields.Char(string = 'URL del servidor de Moodle', config_parameter='atenea.moodle_url')

    validations_path = fields.Char(string = 'Carpeta de almacenamiento de las convalidaciones', config_parameter='atenea.validations_path')