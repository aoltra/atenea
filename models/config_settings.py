# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aules_user = fields.Char(string = "Usuario acceso a Aules")
    password_user = fields.Char(string = "Password acceso a Aules")