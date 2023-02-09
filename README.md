# Atenea

Módulo Odoo para la gestión interna del [CEEDCV](https://portal.edu.gva.es/ceedcv/) (Centro Específico de Educación a Distancia de la Comunidad Valenciana)

_Atenea_ es un módulo para Odoo que proporciona herramientas para simplificar el trabajo diario tanto del equipo directivo como del profesorado y personal administrativo de un centro de educación a distancia de Ciclos Formativos.

Permite:

- Generación automática del calendario escolar
- Envio automatizado de información sobre el centro a los nuevos profesores
- Automatización completa del proceso de convalidaciones
- Automatización del proceso administrativo de los PFC

## Configuración desarrollo

### Requerimientos previos

- python >= 3.8
- pip >= 20.0  

```
 sudo apt install python3-pip
```
- pythonvenv >= 3.8 

```
 sudo apt install python3.8-venv
```

### Configuración

1. Crear entorno virtual. Desde la carpeta del proyecto:
```
python3 -m venv atenea-env
```

2. Activar el entorno virtual. Desde la carpeta del proyecto
```
source atenea-env/bin/activate
```

3. Instalar los paquetes de desarrollo
```
pip install -r requirements-dev.txt
```

4. Instalar el git _commit-msg_ hook
```
gitlint install-hook
```
| Nota 1: _gitlint_ no puede trabajar con otros _commit-msg_ hook
| Nota 2: VScode Error. Es posible que desde VSCode no encuentre _gitlint_ ya que no ejecuta los hoooks teniendo en cuenta el entono virtual creado. Para salucionarlo 