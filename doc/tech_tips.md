# Consejos técnicos de ayuda al desarrollo

## Información interna sobre la base de datos

### Cómo conectar mediante el cliente _psql_ a la base de datos

1. Acceso al contenedor de la base datos

```
docker exec -it atenea_v0_db_1 psql -U odoo -W CEED
```
2. Solicita el password (odoo)

3. Para ver las tablas __/dt__

4. Para ver datos realzar un __select__

## Cómo acceder a _odoo shell_

Conexión a _oddo shell_ dentro del contendor docker

```
docker exec -it nombre_contenedor odoo shell -d CEED --db_host db --db_user odoo -w odoo
```

donde _nombre_contenedor_ es el nombre del contenedor en el que corre _odoo_. Conviene obtenerlo mediante

```
docker ps
```