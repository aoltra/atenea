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

  # simulación de un One2one
  # en user hay un many2one y aqui un one2many
  user_ids = fields.One2many('res.users', 'employee_id')
  # creo un campo que obtenga su valor y que pueda darle valor al employee_id 
  # a partir de user_ids
  user_id = fields.Many2one('res.users', 
                            compute = '_compute_user_id', 
                            inverse = '_user_inverse')
  
  #dni = fields.Char(string = 'DNI', size = 9, required = True)
  name = fields.Char(string = 'Nombre', required = True)
  surname = fields.Char(string = 'Apellidos', required = True)
  phone_extension = fields.Char(string = "Extensión", size = 6)
  work_email = fields.Char(string = 'Email', related = 'user_id.email')

  employee_type = fields.Selection([
        ('profesor', 'Profesor/a'),
        ('pas', 'PAS'),
        ], string ='Tipo de empleado', default = 'profesor', required = True,
        help = "Permite categorizar a los empleados en profesores o personal de administración.")

  
  # sustituciones. Simulo un One2one con dos many2one, un one2many y funciones calculadas
  sick_leave = fields.Boolean(default = False)
  replaced_by_id = fields.Many2one('atenea.employee', string='Sustituye a', 
                                    compute='_compute_teacher', 
                                    inverse='_teacher_inverse')
  replaces_id = fields.Many2one('atenea.employee', string='Sustituye a')
  replaced_by_ids = fields.One2many('atenea.employee', 'replaces_id')
  
  departament_ids = fields.Many2many('atenea.departament', required = True, string = 'Departamentos')
  roles_ids = fields.Many2many('atenea.rol', string = 'Cargos')
  
  active = fields.Boolean('Activo', related='user_id.active', help = 'Indica si el usuario Atenea asociado está activo')

  @api.depends('user_ids')
  def _compute_user_id(self):
    """
    Asigna el usuario como primer elemento de la relación doble uno a muchos
    """
    for record in self:
      if len(record.user_ids) > 0:
        record.user_id = record.user_ids[0] 

  def _user_inverse(self):
    """
    En el caso de que el user_id cambie, se modifica el employee_id de ese user_id
    """
    for record in self:
      if len(record.user_ids) > 0:
        # borramos la referencia previa
        user = record.env['res.users'].browse(record.user_ids[0].id)
        user.employee_id = False
    
      record.user_id.employee_id = record

  @api.depends('replaced_by_ids')
  def _compute_teacher(self):
    for record in self:
      if len(record.replaced_by_ids) > 0:
        record.replaced_by_id = record.replaced_by_ids[0]

  def _teacher_inverse(self):
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