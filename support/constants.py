# -*- coding: utf-8 -*-

########################
#####  Matricula aula de tutoria
########################

# El plazo de convalidaciones está abierto
VALIDATION_PERIOD_OPEN = 0

# campos del anexo del pdf que son obligatorios
# las listas indican obligatoriedad de todos los elementos
# las tuplas indican obligatoriedad de al menos uno
PDF_VALIDATION_FIELDS = [ 
      ('A_Apellidos', 'Apellidos'),
      ('A_Nombre', 'Nombre'),
      ('A_NIA', 'NIA, Número de Identificacion del Alumno/a'),
      (('B_requisito1', 'B_requisito2', 'B_requisito3', 'B_requisito4', 'B_requisito5'), 'Requisitos reunidos'),
      (('C_docu1', 'C_docu2', 'C_docu3', 'C_docu4', 'C_docu4_2'), 'Documentación aportada'),
      (('C_modulo1', 'C_modulo2', 'C_modulo3', 'C_modulo4', 'C_modulo5', 'C_modulo6'), 
      #'C_modulo7', 'C_modulo8', 'C_modulo9', 'C_modulo10', 'C_modulo11', 'C_modulo12'), 
      'Módulo/s a convalidar o solicitar su aprobado con anterioridad'),
      ('C_firma_dia', 'Día de la firma'),
      ('C_firma_mes', 'Mes de la firma'),
      ('C_firma_anyo', 'Año de la firma'),
      ('C_firma_ciudad', 'Ciudad de la firma')]