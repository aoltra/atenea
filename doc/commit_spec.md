# Especificación de commits

Se elige la especificación de commits [convencionales](https://www.conventionalcommits.org/en/v1.0.0/), que tiene como formato

>  type(scope?): message

Por ejemplo:

_feat(core): versionado de calendario_

## Tipos de commit

Lista de tipos de commit y abreviatura a utilizar

| Nombre | tipo |  descripción |
| :-- | :-------:  |  :--------- | 
| build | _build_  | Modificación o creación archivos elementos que afectan a la infraestructura de desarrollo, requirements, package.json, etc |
| feature | _feat_ |  Nueva característica |
| fix | _fix_  | Error corregido |
| documentos | _docs_ | Actualización de documentación |
| continuos integration | _ci_ | Cambios en los ficheros referidos a la integración/despliegue continuo |
| refact | _rfct_ | Refactorización de código | 
| style | _style_ | Corrección linter o formato. En general cualquier cosa que no afecte al significado del código | 
| test | _test_ |  Cualquier cosa relacionada con testing |
| performance | _perf_ | Cambio para mejorar el rendimiento |
| work in progress | _wip_ | Trabajo sin finalizar |

<br/>

Tipos basados en la [convenciones](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type) de Angular.

## Contextos

Definen el ámbito en el que se ha realizado el commit

| Nombre | tipo |  descripción |
| :-- | :-------:  |  :--------- | 
| core | (_core_)  | Núcleo de la aplicación |
| proyecto fin de ciclo | (_pfc_)  | Desarrollo del PFC |
| convalidaciones | (_valid_)  | Proceso de convalidaciones  |
