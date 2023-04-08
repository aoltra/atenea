# Cómo colaborar en el proyecto

## Requisitos

1. Disponer de una cuenta de [GitHub](www.github.com)
2. Solicitar invitación como colaborador vía mail
3. Aceptar la invitación como colaborador

 > Es recomendable realizar la conexión [a través de SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

## Configuración

1. Ejecutar Odoo via Docker compose 

... In progress

2. Desde la carpeta _volumesOdoo/addons_, crear una carpeta _atenea_ y posicionarse en su interior

   ```
   > mkdir atenea
   > cd atenea  
   ```

3. Inicializar un repositorio git

   ``` 
   > git init
   ```

   > No se opta por clonar para evitar incluir la rama _main_

4. Incluir el remoto _origin_

   ``` 
   > git remote add origin git@github.com:aoltra/atenea.git 
   ``` 

5. Crear y posicionarse en una rama llamada _dev_

   ``` 
   > git checkout -b dev
   ```

6. Traer el código de _origin/dev_ (los deja en la rama local actual, en este caso _dev_)

   ``` 
   > git pull origin dev
   ```

## Cómo trabajar

Para cada una de las tareas a realizar hay que crearse un rama, en la que irán todos los commits relacionados con esa tarea/desarrollo.

1. Poner al día _dev_. Desde la rama _dev_

   ```
   > git pull origin dev
   ```   

2. Desde _dev_ crear una rama y posicionarse en ella para el desarrollo del código. La rama tendrá como nomenclatura:

   _tipo_módulo_descripción_
 
   Dónde:

   * tipo: cualquiera de los tipos descritos en [commit_spec](./commit_spec.md)
   * módulo: cualquiera de los contextos descritos en [commit_spec](./commit_spec.md)
   * descripción: nombre de la característica o número de issue 

   Por ejemplo, desde la rama _dev_:

   ```
   > git checkout -b fix_core_34
   ```

   > No todos los commits de ese desarrollo tienen porque ser del mismo tipo que la rama

3. Crear todos los commits necesarios en local.

## Pull Request

Una vez finalizada la tarea hay que solicitar un pull request para que el código se incluya en la rama _main_ del repo.

1. Hacer un _push_ de la rama a _origin_

   ```
   > git push origin fix_core_34
   ```

2. Cuando la tarea esté acabada, desde Github, hacer un _pull request_, documentándolo correctamente para que el revisor tenga toda la información. El PR se hace sobre la rama _dev_ y hay que rellenar los datos sobre revisor, a quién está asignado y si está vinculado a una tarea del proyecto o issue

3. El revisor aprueba, comenta o requerirá cambios.


## Consejos

  * Hacer commits concretos y con mensajes claros (ver [commit_spec](./commit_spec.md)).
  * Duración de la ramas cortas en el tiempo. Si una característica es muy larga es preferible dividirla en subcaracterísticas.
  * Poner al día _dev_ antes de empezar.
  * Para solucionar posibles conflictos de la manera más sencilla, es conveniente antes de hacer el push de la rama, hacer un pull de _dev_ a la rama de trabajo

    ```
    > git pull origin dev
    ```
  
  * Aunque no es lo habitual, si varios programadores trabajan en la misma tarea, es decir, en la misma rama, es conveniente poner también al día esa rama (puede exigir la resolución de conflictos)

   ```
   > git pull origin fix_core_34
   ```
 
## Cómo testear el PR

Para testear y aprobar el código del PR, los pasos son:

1. Obtener la pseudo-rama del PR y darle un nombre de rama local, por ejemplo pr20:
   
    ```
   > git fetch origin pull/20/head:pr20
    ```

2. Posicionarse en esa rama

   ```
   > git checkout pr20
   ```

3. Hacer las pruebas


En caso que querer modificar el código del PR, se pueden realizar todos los commits que se consideren y posteriormente subirlos 

  ```
  > git pull upstream pull/20/head
  ```