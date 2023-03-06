#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Añade al fichero de tokens un nuevo token de usuario
Necesita de la instalación libcurl4-openssl-dev y libssl-dev
"""
import sys
import os
import pickle
import json
import pycurl

from io import BytesIO
from urllib.parse import urlencode

print('\033[1mAtena. Almacena un token de acceso a moodle\033[0m')

if len(sys.argv) < 2:
  try:
    with open('moodle_host.txt') as f:
      moodle_host = list(line for line in f)[0]
  except FileNotFoundError:
    print('\033[0;31m[ERROR]\033[0m MOODLE_HOST o fichero moodle_host.txt no definido') 
    print('Uso: save_token_moodle.py MOODLE_HOST')
    print('     save_token_moodle.py   (y moodle host definido en fichero moodle_host.txt)s')
    exit()
else:
  moodle_host = sys.argv[1]

print('\033[0;32m[INFO]\033[0m IMPORTANTE: Este script debe ejecutarse en la máquina o contenedor HOST')
print('\033[0;32m[INFO]\033[0m La contraseña solicitada no es almacenada. Sólo se utiliza para obtener el token de acceso a Moodle')
print('\033[0;32m[INFO]\033[0m IMPORTANTE: El token permite a Atenea conectarse a {} como si se tratara del usuario.'.format(moodle_host))
print('\033[0;32m[INFO]\033[0m Atenea no se conecta en nombre del usuario a ningún otro servicio.')

confirm = input('¿Desea continua? (s/n) ')

if confirm.upper() != 'S':
  print('\033[0;31m[ERROR]\033[0m Proceso de grabación de tokens cancelado')
  exit()

atenea_user = input('Usuario Atenea: ')
moodle_user = input('Usuario Moodle: ')
moodle_pass = input('Contraseña Moodle: ')

users_tokens = {}

try:
  with open(os.path.expanduser("~/.atenea_moodleteacher"), "rb") as f:
    users_tokens = pickle.load(f)
except Exception:
  print('\033[0;32m[INFO]\033[0m Fichero .atenea_moodleteacher no encontrado. Creando uno nuevo...')

print('\033[0;32m[INFO]\033[0m Número de tokens actuales:', len(users_tokens))
  
# si el usuario ya existe se avisa de que será eliminado
if atenea_user in users_tokens:
  print('\033[0;32m[INFO]\033[0m El usuario "{}" ya existe. Si continua se eliminará el registro previo.'.format(atenea_user))
  confirm = input('¿Desea continua? (s/n) ')

  if confirm.upper() == 'S':
    del users_tokens[atenea_user]
    print('\033[0;32m[INFO]\033[0m Número de tokens actuales:', len(users_tokens))
  else:
    print('\033[0;31m[ERROR]\033[0m Proceso de grabación de tokens cancelado')
    exit()

print('\033[0;32m[INFO]\033[0m Conectando con', moodle_host)

# obtención del token vía CURL
buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, moodle_host + '/login/token.php?service=moodle_mobile_app')
post_data = {'username': moodle_user, 'password': moodle_pass}
postfields = urlencode(post_data)
c.setopt(c.POSTFIELDS, postfields)
c.setopt(c.WRITEDATA, buffer)

c.perform()
c.close()

response = buffer.getvalue().decode('utf-8')
info_token = json.loads(response)

if 'token' in info_token:
  users_tokens[atenea_user] = info_token['token']
else:
  print('\033[0;31m[ERROR]\033[0m El usuario o la contraseña de Moodle no es correcta.')  
  exit();

try:
  with open(os.path.expanduser("~/.atenea_moodleteacher"), "wb") as f:
    pickle.dump(users_tokens, f)

  print('\033[0;32m[INFO]\033[0m FIchero .atenea_moodleteacher actualizado correctamente.')

except Exception:
  print('\033[0;31m[ERROR]\033[0m No se ha podido crear el fichero .atenea_moodleteacher.')


