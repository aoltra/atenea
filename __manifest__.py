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
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/course.xml',
        'data/departament.xml',
        'data/rol.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
}
