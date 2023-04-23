# -*- coding: utf-8 -*-

from odoo import fields, models


class Users(models.Model):
  _inherit = 'res.users'

  employee_id = fields.Many2one('atenea.employee')

    
