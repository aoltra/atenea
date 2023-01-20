# -*- coding: utf-8 -*-
import re
from odoo import api, models, fields
from odoo.exceptions import ValidationError

class Employee(models.Model):
  """
  Define un empleado del centro
  """

  _name = 'atenea.employee'
  _description = 'Empleado del centro (profesor o administrativo)'
  _order = 'surname'

  user_id = fields.Many2one('res.users')

  #dni = fields.Char(string = 'DNI', size = 9, required = True)
  name = fields.Char(string = 'Nombre', required = True)
  surname = fields.Char(string = 'Apellidos', required = True)
  phone_extension = fields.Char(string = "Extensión", size = 6)
  work_email = fields.Char(string = 'Email')

  employee_type = fields.Selection([
        ('profesor', 'Profesor/a'),
        ('pas', 'PAS'),
        ], string ='Tipo de empleado', default = 'profesor', required = True,
        help = "Tipo de empleado. Permite categorizar a los empleados en profesores o personal de administración.")

  
  # sustituciones. Simulo un One2one con dos many2one, un one2many y funciones calculadas
  sick_leave = fields.Boolean(default = False)
  replaced_by_id = fields.Many2one('atenea.employee', string='Sustituye a', compute='compute_teacher', inverse='teacher_inverse')
  replaces_id = fields.Many2one('atenea.employee', string='Sustituye a')
  replaced_by_ids = fields.One2many('atenea.employee', 'replaces_id')
  

  departament_ids = fields.Many2many('atenea.departament', required = True, string = 'Departamentos')
  roles_ids = fields.Many2many('atenea.rol', string = 'Cargos')
  
  #active = fields.Boolean('Activo', related='resource_id.active', default = True, store = True, readonly = False)

  @api.depends('replaced_by_ids')
  def compute_teacher(self):
    for record in self:
      if len(record.replaced_by_ids) > 0:
        record.replaced_by_id = record.replaced_by_ids[0]

  def teacher_inverse(self):
    for record in self:
      if len(record.replaced_by_ids) > 0:
        # delete previous reference
        teacher = self.env['atenea.employee'].browse(record.replaced_by_ids[0].id)
        teacher.replaces_id = False
      # set new reference
      record.replaced_by_id.replaces_id = record

  @api.onchange('work_email')
  def validate_mail(self):
    if self.work_email:
      match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.work_email)
      if match == None:
        raise ValidationError('email no válido')