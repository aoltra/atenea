# -*- coding: utf-8 -*-
{
    'name': "Atenea",
    'version': '0.0.1a',

    'summary': """
        Módulo para la gestión interna del CEED (Ciclos Formativos)""",

    'description': """
        Módulo que simplifica y atomatiza el trabajo de un centro de Ciclos Formativos a distancia.

        Características principales:
         - Gestión de convalidaciones,
         - Gestión de exenciones, 
         - Generación automática de calendiario escolar
         - Gestión administrativa del PFC
         ...
    """,

    'website': "https://portal.edu.gva.es/ceedcv/",
    'author': 'CEEDCV',
    'maintainer': 'Alfredo Oltra <alfredo.ptcf@gmail.com>',
    'company': 'GVA',
    'category': 'Productivity',

    'license': 'AGPL-3',
    # precio del módulo
    'price': 0,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # external dependencies that have to be installed. Can be python or bin dependencies
    # Only checks whether the dependency is installed. Not install the dependency!!
    'external_dependencies': {
       'python': ['moodleteacher', 'toolz'],
    },
    # always loaded
    'data': [
        # seguridad
        'security/security_groups.xml',
        'security/ir.model.access.csv',  # politicas de acceso generales (todo abierto)
        'security/validation_access.xml',   # politicas de acceso a convalidaciones (reescribe las anteriores)
        # vistas
        'views/views.xml',
        'views/templates.xml',
        'views/config_settings_view.xml',
        # configuración de serie
        'data/config/config_data.xml',
        'data/config/outgoing_mail.xml',
        # datos de modelos
        'data/school.xml',
        'data/departament.xml',
        'data/classroom.xml',
        'data/course.xml',
        'data/subject.xml',
        'data/task_moodle.xml',
        'data/rol.xml',
        # reports
        'reports/custom_footer.xml',
        'reports/school_calendar.xml',
        'reports/pfc_calendar.xml',
        'reports/paper_format.xml',     # el último del bloque
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
}
