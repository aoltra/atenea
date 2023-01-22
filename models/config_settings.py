# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aules_user = fields.Char(string = 'Usuario acceso a Aules', config_parameter='atenea.aules_user')
    aules_password = fields.Char(string = 'Password acceso a Aules', config_parameter='atenea.aules_password')