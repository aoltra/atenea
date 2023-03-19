# Consejos técnicos de ayuda al desarrollo

## Información interna sobre la base de datos

### Cómo conectar mediante el cliente _psql_ a la base de datos

1. Acceso al contenedor de la base datos

```
docker exec -it atenea_v0_db_1 psql -U odoo -W CEED
```
2. Solicita el password (odoo)

3. Para ver las tablas __\dt__

4. Para ver datos realizar un __select__

## Cómo acceder a _odoo shell_

Conexión a _oddo shell_ dentro del contendor docker

```
docker exec -it nombre_contenedor odoo shell -d CEED --db_host db --db_user odoo -w odoo
```

donde _nombre_contenedor_ es el nombre del contenedor en el que corre _odoo_. Conviene obtenerlo mediante

```
docker ps
```

## Cómo acceder a los informes HTML desde el navegador

Hay que acceder a la URL 

http://localhost:8069/report/html/[modulo].[nombre informe]/[id]

Por ejemplo

http://localhost:8069/report/html/atenea.report_school_calendar/1

__Nota__: Es necesario estar logueado en otra pestaña en Odoo

## Cómo obtener el token de acceso a Moodle

Para poder conectar con Moodle desde Atenea es necesario un token de autenticación. El token se consigue haciendo una petición al _servicio moodle_mobile_app_

```
curl -d username="USERNAME" -d password="PASSWORD" 'https://aules.edu.gva.es/ed/login/token.php?service=moodle_mobile_app'
```

## Cómo hacer peticiones CURL a Moodle

```
curl "https://your.site.com/webservice/rest/server.php?wstoken=...&wsfunction=...&moodlewsrestformat=json"
```

Seguido de los parámetros necesarios

```
curl https://localhost/webservice/rest/server.php?wstoken=abcdef012345678&wsfunction=mod_assign_set_user_flags&moodlewsrestformat=json&assignmentid=1&userflags[0][locked]=1&userflags[0][userid]=5
```

> Nota: en el caso de hacer peticiones al moodle de docker utilizar http el nular de https