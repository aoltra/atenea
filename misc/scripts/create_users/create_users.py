#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import csv
import sys

print('\033[1mAtena. Crea usuarios y empleados desde csv\033[0m')

url = "http://localhost:8069"
db = "CEED"
username = 'admin'
password = 'admin'
users = []
employees = {}

if len(sys.argv) < 2:
  print('\033[0;31m[ERROR]\033[0m Fichero csv de usuarios no definido')
  print('    Uso: create_users.py fichero.csv')
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
      users.append({
          'name': '%s %s' % (row[0], row[1]),
          'login': row[2],
          'lang': row[3],
          'company_ids':[1],
          'company_id': 1,
          'email': row[2]
          # 'new_password': el password no se inserta por motivos de seguridad
      })
      employees[row[2]] = { 'name': row[0],
          'surname': row[1],
          'employee_type': row[5],
          'departament_ids': row[4]
      }
    line_count += 1

print('\033[0;32m[INFO]\033[0m Usuarios en csv:', len(users))    

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# obtengo todos los departamentos
departaments_output = models.execute_kw(db, uid, password, 'atenea.departament', 'search_read', [[]], { 'fields': ['id', 'name']})
departaments = {}
for dep in departaments_output:
  departaments[dep['name']] = dep['id']


print(departaments)

""" 

user_id=models.execute_kw(db, uid, password, 'res.users', 'create', 
[{'name':"userAPI9", 'login':'userapi2@gmail.com', 'new_password':'123456'}]) 
'company_id':1, 'company_ids':[1], 'sel_groups_39_40':40,    'sel_groups_9_44_10':10, 'sel_groups_29_30':30, 'sel_groups_36_37':37, 'sel_groups_21_22_23':23,'sel_groups_5':5
 """
try:
  inactive_users = models.execute_kw(db, uid, password, 'res.users', 'search_read', [[['active','=', False]]], { 'fields': ['id', 'login']})
  print(inactive_users)
except (xmlrpc.client.Fault) as e:
  print('\033[0;31m[ERROR]\033[0m ' + e.faultString)
  print(f'\033[0;32m[INFO]\033[0m Saliendo...')
  exit()


line_count_OK = 0
line_count_ERROR = 0

for user in users:  
  print("\033[0;32m[INFO]\033[0m Procesando ", user)
  try:
    # Esta en Atenea pero esta inactivo
    odoo_user = next((item for item in inactive_users if item['login'] == user['login']), None)

    if odoo_user == None: # no está inactivo en Atenea 
      # se crea. En caso de que ya exista salta una excepción
      id = models.execute_kw(db, uid, password, 'res.users', 'create', [user])
      employees[user['login']]['user_id'] = id
      employees[user['login']]['departament_ids'] = [(4, departaments[employees[user['login']]['departament_ids']])]
      models.execute_kw(db, uid, password, 'atenea.employee', 'create', [employees[user['login']]])
    else: # está pero inactivo
      print(f'\t\033[0;32m[INFO]\033[0m {user["name"]} ({user["login"]}) ya existe en Atenea. Activandolo')
      models.execute_kw(db, uid, password, 'res.users', 'write', [[odoo_user['id']], {'active': True}])
   
    line_count_OK += 1
  except (xmlrpc.client.Fault) as e:
    print('\t\033[0;31m[ERROR]\033[0m ' + e.faultString)
    line_count_ERROR += 1
  except KeyError:
    print('\t\033[0;31m[ERROR]\033[0m Clave no encontrada. Posiblemente el departamento no existe')
    line_count_ERROR += 1
  
print(f'\033[0;32m[INFO]\033[0m Procesados {line_count_OK} usuarios / Errores: {line_count_ERROR}.')


