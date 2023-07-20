#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import csv
import sys

print('\033[1mAtenea. Crea los datos de las aulas virtuales desde un csv\033[0m')

url = "http://localhost:8069"
db = "CEED"
username = 'admin'
password = 'admin'

classrooms = []

if len(sys.argv) < 2:
  print('\033[0;31m[ERROR]\033[0m Fichero csv de aulas no definido')
  print('    Uso: create_classrooms.py fichero.csv')
  exit()

# end point xmlrpc/2/common permite llamadas sin autenticar
print('\033[0;32m[INFO]\033[0m Conectando con',url)
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print('\033[0;32m[INFO]\033[0m Odoo server', common.version()['server_version'])
# autenticación
uid = common.authenticate(db, username, password, {})

with open(sys.argv[1]) as csv_file:
  csv_reader = csv.reader(csv_file, delimiter = ',')
  line_count = 0
  for row in csv_reader:
    if line_count > 0:
      # print(line_count, row)
      classrooms.append({
          'code': row[1],
          'description': row[2],
          'moodle_id': row[0],
          'lang_id': row[3]
      })
    line_count += 1

print('\033[0;32m[INFO]\033[0m Aulas en csv:', len(classrooms))    

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# obtengo todos los ciclos
courses_output = models.execute_kw(db, uid, password, 'atenea.course', 'search_read', [[]], { 'fields': ['id', 'code', 'abbr', 'name']})
courses = {}
for cur in courses_output:
  courses[cur['code']] = {'id': cur['id'], 'abbr':cur['abbr'], 'name': cur['name']  }

print(f'\033[0;32m[INFO]\033[0m Ciclos:')
print(f'   {courses}')

# obtengo todos los módulos
subjects_output = models.execute_kw(db, uid, password, 'atenea.subject', 'search_read', [[]], { 'fields': ['id', 'code', 'abbr', 'name']})
subjects = {}
for sub in subjects_output:
  subjects[sub['code']] = {'id': sub['id'], 'abbr':sub['abbr'],  }

print(f'\033[0;32m[INFO]\033[0m Módulos:')
print(f'   {subjects}')

# idiomas activos
languages_output = models.execute_kw(db, uid, password, 'res.lang', 'search_read', [[['active','=', True]]], { 'fields': ['id','code']})
languages = []
for lang in languages_output:
  languages.append(lang['code'])

print(f'\033[0;32m[INFO]\033[0m Idiomas:')
print(f'   {languages_output}')

line_count_OK = 0
line_count_ERROR = 0

try:
  current_classrooms = models.execute_kw(db, uid, password, 'atenea.classroom', 'search_read', [[]], { 'fields': ['id', 'code']})
  print(f'\033[0;32m[INFO]\033[0m Classroom existentes:')
  print(f'   {current_classrooms}')
except (xmlrpc.client.Fault) as e:
  print('\033[0;31m[ERROR]\033[0m ' + e.faultString)
  print(f'\033[0;32m[INFO]\033[0m Saliendo...')
  exit()

for classroom in classrooms:
  print("\033[0;32m[INFO]\033[0m Procesando ", classroom['code'])
  try:
    if classroom['lang_id'] not in languages:
      print(f'   \033[0;31m[ERROR]\033[0m ({classroom["code"]}) {classroom["lang_id"]} no existe o no está activo en Atenea. Asignando idioma por defecto {languages[0]}.')
      classroom['lang_id'] = languages[0]

    classroom_lang = next((lang['id'] for lang in languages_output if lang['code'] == classroom['lang_id']),None)

    # Está en Atenea
    classroom_exist = next((item for item in current_classrooms if item['code'] == classroom['code']), None)
    
    code_blocks = classroom['code'].split('_')

    if classroom_exist == None: # no está ya en Atenea 
      classroom['lang_id'] = classroom_lang
      classroom['description'] = f'Aula de {classroom["description"]} ({courses[code_blocks[4]]["abbr"]})' 
      classroom_id = models.execute_kw(db, uid, password, 'atenea.classroom', 'create', [classroom])
    else: # ya está en Atenea
      print(f'   \033[0;32m[INFO]\033[0m {classroom["code"]} ya existe en Atenea. Actualizándolo')
      
      models.execute_kw(db, uid, password, 'atenea.classroom', 'write', [[classroom_exist['id']], {'description': classroom['description'], 'lang_id': classroom_lang , 'moodle_id': classroom['moodle_id']}])
      classroom_id = classroom_exist['id']
    
    # relación con módulos
    
    rel_id = models.execute_kw(db, uid, password, 'atenea.subject_classroom_rel', 'create', [{
        'course_id': courses[code_blocks[4]]['id'],
        'subject_id': subjects[code_blocks[5]]['id'],
        'classroom_id': classroom_id
        }])
    
    line_count_OK += 1
    print(f'   \033[0;32m[INFO]\033[0m Asociado {classroom["code"]} con el módulo {subjects[code_blocks[5]]["abbr"]} en {courses[code_blocks[4]]["abbr"]}')

  except (xmlrpc.client.Fault) as e:
    print('   \033[0;31m[ERROR]\033[0m ' + e.faultString)
    line_count_ERROR += 1
  except KeyError:
    print('   \033[0;31m[ERROR]\033[0m Clave no encontrada.')
    line_count_ERROR += 1

print(f'\033[0;32m[INFO]\033[0m Procesados {line_count_OK} aulas virtuales / Errores: {line_count_ERROR}.')
print(f'\033[0;32m[INFO]\033[0m Hay que repasar y asignar las aulas de inglés técnico con los módulos correspondientes.')