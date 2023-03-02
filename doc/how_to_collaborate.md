# Como colaborar en el proyecto

## Requisitos

1. Disponer de una cuenta de [GitHub](www.github.com)
2. Solicitar invitación como colaborador vía mail
3. Aceptar la invitación como colaborador

 > Es recomendable realizar la conexión [a través de SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

## Configuración

1. Ejecutar Odoo via Docker compose 

... In progress

2. Desde la carpeta _volumesOdoo/addons_

   ``` 
   git clone https://github.com/aoltra/atenea.git atenea_dev
   ```

3. Seguirlos pasos indicados en README.md


## Desarrollo

1. Tener el local (carpeta _atenea_dev_) al día

   ``` 
   git pull main
   ```

2. Crear una rama y posicionarse en ella para el desarrollo del código. La rama tendrá como nomenclatura:

   _tipo_módulo_descripción_
 
   Dónde:

   * tipo: cualquiera de los tipos descritos en [commit_spec](./commit_spec.md)
   * módulo: cualquiera de los contextos descritos en [commit_spec](./commit_spec.md)
   * descripción: nombre de la característica o número de issue 

   Por ejemplo:

   ```
   git checkout -b fix_core_34
   ```

   > No todos los commits de ese desarrollo tienen porque ser del mismo tipo que la rama

  ## Pull Request

  Una vez finalizado la tarea hay que solicitar un pull request para que el código se incluya en la rama main del repo.

  1. Hacer un _push_ de la rama a _origin_

     ```
     git push fix_core_34
     ```

  2. Cuando la tarea esté acabada, desde Github, hacer un _pull request_, documentándolo correctamente para que el revisor tenga toda la información. Hay que rellenar los datos sobre revisor, a quién está asignado y si está vinculadao a una tarea del proyecto o issue.

  3. El revisor aprueba, comenta o requerirá cambios.

  ## Consejos

  * Hacer commits concretos y con mensajes claros (ver [commit_spec](./commit_spec.md)).
  * Duración de la ramas cortas en el tiempo. Si una característica es muy larga es preferible dividirla en subcaracterísticas.
  * Poner al día _main_ antes de empezar
  * Si varios programadores trabajan en la misma tarea, es decir, en la misma rama, es conveniente poner también al día esa rama (puede exigir la resolución de conflictos)