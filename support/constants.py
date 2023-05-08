# -*- coding: utf-8 -*-

########################
#####  Matricula aula de tutoria
########################

# El plazo de convalidaciones está abierto
VALIDATION_PERIOD_OPEN = 0

# campos del anexo del pdf que son obligatorios
# las listas indican obligatoriedad de todos los elementos
# las tuplas indican obligatoriedad de al menos uno
PDF_VALIDATION_FIELDS_MANDATORY = [ 
      ('A_Apellidos', 'Apellidos'),
      ('A_Nombre', 'Nombre'),
      ('A_NIA', 'NIA, Número de Identificacion del Alumno/a'),
      (('B_Requisito1', 'B_Requisito2', 'B_Requisito3', 'B_Requisito4', 'B_Requisito5'), 'Requisitos reunidos'),
      (('C_Docu1', 'C_Docu2', 'C_Docu3', 'C_Docu4', 'C_Docu5'), 'Documentación aportada'),
      (('C_Modulo1', 'C_Modulo2', 'C_Modulo3', 'C_Modulo4', 
        'C_Modulo5', 'C_Modulo6', 'C_Modulo7', 'C_Modulo8', 
        'C_Modulo9', 'C_Modulo10', 'C_Modulo11', 'C_Modulo12',
        'C_Modulo13', 'C_Modulo14', 'C_Modulo15', 'C_Modulo16'), 
      'Módulo/s a convalidar o solicitar su aprobado con anterioridad'),
      ('C_Dia', 'Día de la firma'),
      ('C_Mes', 'Mes de la firma'),
      ('C_Anyo', 'Año de la firma'),
      ('C_Ciudad', 'Ciudad de la firma')]

# campos del anexo pdf de convalidaciones que deben ir juntos
# no puede haber valor en el primer item si lo hay en el segundo
PDF_VALIDATION_FIELDS_PAIRED = [ 
      ('C_Modulo1', 'C_Modulo1AACO'),
      ('C_Modulo2', 'C_Modulo2AACO'),
      ('C_Modulo3', 'C_Modulo3AACO'),
      ('C_Modulo4', 'C_Modulo4AACO'),
      ('C_Modulo5', 'C_Modulo5AACO'),
      ('C_Modulo6', 'C_Modulo6AACO'),
      ('C_Modulo7', 'C_Modulo7AACO'),
      ('C_Modulo8', 'C_Modulo8AACO'),
      ('C_Modulo9', 'C_Modulo9AACO'),
      ('C_Modulo10', 'C_Modulo10AACO'),
      ('C_Modulo11', 'C_Modulo11AACO'),
      ('C_Modulo12', 'C_Modulo12AACO'),
      ('C_Modulo13', 'C_Modulo13AACO'),
      ('C_Modulo14', 'C_Modulo14AACO'),
      ('C_Modulo15', 'C_Modulo15AACO'),
      ('C_Modulo16', 'C_Modulo16AACO')  ]

PDF_FIELD_VALUE = 0
PDF_FIELD_TYPE = 1