## Requerimientos

Para el correcto funcionamento de Maya con Moodle, es necesario:

1. [ ] Versión 3.9 o superior
2. [ ] Permitir acceso vía móvil (_API Rest_)

    Como _administrador_:

       Site administration / site administration / Moodle App / Mobile settings -> Enable web services =  True

3. [ ] Disponer de todas las aulas virtuales asociadas a los módulos. 

    * Las aulas pueden tener como nombre el que quiera siempre y cuando acaben en *_CICLO_MODULO*, donde _CICLO_ es el código del ciclo y _MODULO_ el código del módulo, por ejemplo SEG9_CEE_46025799_2022_845104_0615. 
    * En caso de las aulas de tutoria los código deben ser _TUT1_ y _TUT2_ dos para las tutorias de primero y segundo respectivamente.
    * Es recomendable, aunque no indispensable, que las aulas de tutoría se agrupen por ciclos formativos. En ese caso el código será _TUT0_.
    * Este formato sigue la denominación de las aulas de Aules

        > No es un formato muy recomendable ya que limita la usabilidad de los alumnos en el acceso a la información vía correo electrónico. Posiblemente sería más interesante que _CICLO_MODULO fuerán las siglas del ciclo y módulo respectivamente más que el código de estos.

4. [ ] Creación de un usuario denominado _maya nombre del centro_ (por ejemplo _Maya CEED_) que se encuentre matriculado con rol de profesor en todas aquellas aulas en las que Maya deba actuar, como mínimo todas las aulas de tutoria.

5. [ ] Matriculación de todos los alumnos en las aulas correspondientes.

   * Todos deben tener asignado el rol _Estudiante_
   * Todos los alumnos del mismo ciclo deben estar matriculados en el aula de tutoria correspondiente.

   

   