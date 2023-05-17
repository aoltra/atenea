# Proceso de instalación/configuración Moodle pruebas

## Acceso administrador

Log In (admin) ->  u: moodle / p: secret

## Activación web services en Moodle

Cómo ususario _administrador_:

Site administration / site administration / Moodle App / Mobile settings -> Enable web services =  True
   
## Recuperación curso 

Site administration / Courses / Courses / Restore course -> arrastrar _/tests/moodle_db/fichero.mbz_
  
  - Restore as a new course -> select category -> Miscellaneous 
  
  - Perfomr restore

## Acceso usuarios Moodle

Aunque están ya creados, es necesario reiniciar sus contraseñas.

Site administration / Users / Accounts / Browse list of users

Se accede a la configuración de cada uno de ellos y se elige un nuevo password, obtenido de la lista siguiente lista

| Login  | Password   | Token |
| :--    | :-------:  | :--------- | 
| atenea | Atenea1;-) | 01f863f89bfdc27446aea4c357d7968b |
| alumno01 | [Alumn0] |    |
| alumno02 | [Alumn0] |    |
| alumno03 | [Alumn0] |    |
| alumno04 | [Alumn0] |    |

## Creación del fichero de acceso desde Atenea

Desde el contenedor odoodock-web-1 abrir un terminal y acceder a la carpeta /mnt/extra-addons/atenea/misc/scripts/save_token_moodle

```
$ docker exec -it odoodock-web-1 bash 
> cd /mnt/extra-addons/atenea/misc/scripts/save_token_moodle
> python3 ./save_token_moodle.py
```

Contestar a las preguntas con:
  - atenea 
  - atenea
  - Atenea1;-)