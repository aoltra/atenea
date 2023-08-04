## Proceso de configuración

Los pasos para la configuración de Odoo son:

  > Es importante haber realizado previamente el proceso de configuracionm de Moodle

  1. [ ] Creación de la base de datos. 

     * Aunque en principio el nombre de la base de datos es indiferente, es recomendable utilizar la nomenclatura *CENTRO_[MOODLE]_CURSO* donde CENTRO son las siglas del centro, [MOODLE] es un parámetro opcional que indica el servidor Moodle con el que se va a trabajar y curso el año de inicio del curso. Por ejemplo: CEED_Aules_2023

       > En caso de bases de datos de pruebas es recomendable empezar el nombre de la base de datos por TEST_: TEST_CEED_Aules_2023

     * Indicar como país _España_

     * Indicar como idioma _Español / España_

     * No crear datos de demo

     * El email es el login del usuario, no es necesario que sea un email. Es habitual utilizar _administrador_

     IMPORTANTE: Es fundamental guardar el _master password_ de la base de datos para futuros procesos.

  2. [ ] Instalar el módulo _Conversaciones_ (_Discuss_)

  3. [ ] Configurar idiomas extras, por ejemplo inglés (UK). De entre estos idiomas, el usuario podrá elegir uno para su entorno y además serán los idiomas posibles en las aulas virtuales.

      Como _administrador_:

         Ajustes / Idiomas / Añadir idioma

  4. [ ] Configurar el formato de fecha al europeo. 
  
      Como _administrador_:

         Ajustes / Idiomas / Administrar idiomas
      
      Para cada uno de los idiomas instalados comprobar (y cambiar en caso contrario) que el formato de fecha sea _%d/%m/%Y_.
  
  5. [ ] Clonar el repo de **Maya | Core** desde [github](https://github.com/aoltra/atenea). Para ello la mejor opción es el uso de script _create-module.sh_, opción O2, tal y como se explica [aquí](https://github.com/aoltra/odoodock#usando-el-script-create-modulesh)

  