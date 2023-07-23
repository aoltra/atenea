#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import csv
import sys

print('\033[1mAtenea. Crea los datos de las tareas que se vinculan con Atenea desde un csv\033[0m')

url = "http://localhost:8069"
db = "CEED"
username = 'admin'
password = 'admin'

tasks_keys = ['validation', 'pfc_1', 'pfc_2', 'cancel', 'renounce']

tasks = []

if len(sys.argv) < 2:
  print('\033[0;31m[ERROR]\033[0m Fichero csv de las tareas no definido')
  print('    Uso: create_tasks.py fichero.csv')
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
      tasks.append({
          'moodle_id': row[0],
          'key': row[1],
          'description': row[2],
          'course_abbr': row[3],
          'classroom_code': row[4]
      })
    line_count += 1

print('\033[0;32m[INFO]\033[0m Tareas en csv:', len(tasks))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

line_count_OK = 0
line_count_ERROR = 0

# obtengo todos los ciclos
courses_output = models.execute_kw(db, uid, password, 'atenea.course', 'search_read', [[]], { 'fields': ['id', 'abbr', 'code']})
courses = {}
for cur in courses_output:
  courses[cur['abbr']] = {'code':cur['code'] }


# matriz para comprobar que tareas están creadas y cuales no de cada ciclo
check_task= {}

for cur in courses:
  check_task[cur] ={}
  for tk in tasks_keys:
    check_task[cur][tk] = False

try:
  current_classrooms = models.execute_kw(db, uid, password, 'atenea.classroom', 'search_read', [[]], { 'fields': ['id', 'code']})
  print(f'\033[0;32m[INFO]\033[0m Classroom existentes:')
  print(f'   {current_classrooms}')
except (xmlrpc.client.Fault) as e:
  print('\033[0;31m[ERROR]\033[0m ' + e.faultString)
  print(f'\033[0;32m[INFO]\033[0m Saliendo...')
  exit()

try:
  current_tasks = models.execute_kw(db, uid, password, 'atenea.task_moodle', 'search_read', [[]], { 'fields': ['id', 'key','classroom_id', 'course_abbr']})
  print(f'\033[0;32m[INFO]\033[0m Tareas existentes:')
  print(f'   {current_tasks}')
except (xmlrpc.client.Fault) as e:
  print('\033[0;31m[ERROR]\033[0m ' + e.faultString)
  print(f'\033[0;32m[INFO]\033[0m Saliendo...')
  exit()

for task in current_tasks:
  check_task[task['course_abbr']][task['key']] = task['classroom_id'][1]

for task in tasks:
  print(f"\033[0;32m[INFO]\033[0m Procesando: {task['description']} / {task['course_abbr']}")

  try:
    # Está en Atenea?
    classroom_id = next((classroom for classroom in current_classrooms if classroom['code'] == task['classroom_code']), None)

    if classroom_id == None:
      print(f'    \033[0;31m[ERROR]\033[0m No se encuentra el id del aula {task["classroom_code"]}')
      line_count_ERROR += 1
      continue
    
    task_exist = next((item for item in current_tasks if item['key'] == task['key'] and item['classroom_id'][0] == classroom_id['id']), None)
    
    if task_exist == None: # no está
      if check_task[task["course_abbr"]][task['key']] != False:
        print(f'    \033[0;31m[ERROR]\033[0m Ya existe una tarea para esa key ({task["key"]}) y ese ciclo ({task["course_abbr"]}) en otra aula ({check_task[task["course_abbr"]][task["key"]]})')
        line_count_ERROR += 1
        continue

      task_id = models.execute_kw(db, uid, password, 'atenea.task_moodle', 'create', [{
          'key': task['key'],
          'description': task['description'],
          'moodle_id': task['moodle_id'],
          'course_abbr': task['course_abbr'],
          'classroom_id': classroom_id['id'] }])
      
      check_task[task["course_abbr"]][task['key']] = classroom_id['code']
      line_count_OK += 1
      
    else: # ya está en Atenea
      print(f'   \033[0;32m[INFO]\033[0m {task["key"]}/{task["course_abbr"]} ya existe en Atenea. Actualizándolo') 
      
      models.execute_kw(db, uid, password, 'atenea.task_moodle', 'write', [[task_exist['id']],
           { 'description': task['description'], 
             'course_abbr': task['course_abbr'],
             'moodle_id': task['moodle_id'] }])
      
      check_task[task["course_abbr"]][task['key']] = True
    
      line_count_OK += 1

  except (xmlrpc.client.Fault) as e:
    print('   \033[0;31m[ERROR]\033[0m ' + e.faultString)
    line_count_ERROR += 1
  except KeyError:
    print('   \033[0;31m[ERROR]\033[0m Clave no encontrada.')
    line_count_ERROR += 1

print(f'\033[0;32m[INFO]\033[0m Procesados {line_count_OK} aulas virtuales / Errores: {line_count_ERROR}.')

print(f'\033        Tabla de tareas por crear')

header_table = '       {:<12}'.format('CICLO')
for ky in tasks_keys:
  header_table += ' {:<12}'.format(ky)

print(header_table)
print('      ' + '-' * (len(header_table) - 7))
for key, value in check_task.items():
  row = '        {:<12}'.format(key)
  for vl in value.values():
    if vl == False:
      row += ' {:<23}'.format('\033[0;31mX\033[0m')
    else:
      row += ' {:<23}'.format('\033[0;32mO\033[0m')
  print(row)

