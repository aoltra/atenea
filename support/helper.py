# -*- coding: utf-8 -*-
import subprocess
import re

import logging
_logger = logging.getLogger(__name__)

def is_set_flag(value, option):
    """
    Devuelve True o False si la opción aparece en el valor
    Por ejemplo: is_set_flag(25, 1) -> True
    Por ejemplo: is_set_flag(25, 2) -> False
    """
    return value & 1 << option != 0

def set_flag(value, option):
    """
    Asigna un uno (pone a True) en la propiedad (posición) indicada 
    Por ejemplo: set_flag(24, 1) -> 25
    """
    return value | (1 << option) 

def unset_flag(value, option):
    """
    Asigna un cero (pone a False) en la propiedad (posición) indicada 
    Por ejemplo: unset_flag(25, 1) -> 24
    """
    return value | ~(1 << option) 

def get_data_from_pdf(pdf_file):
    """
    Obtiene información de los formularios de un pdf
    """
    # Ejecutar pdftk y capturar la salida
    pdftk_command = ['pdftk', pdf_file, 'dump_data_fields_utf8']
    output = subprocess.run(pdftk_command, capture_output = True, text = True, check = True)

    # Procesamos la salida utilizando expresiones regulares
    field_regex = re.compile('FieldType: (.*)\\nFieldName: (.*)\\n(.*\\n|.*\\n.*\\n)FieldValue: (.*)\\n')
    #"FieldName: (.*)\n|FieldValue: (.*)\n"gm

    fields = {}

    for match in field_regex.finditer(output.stdout):
      fields[match.group(2)] = (match.group(4).strip(), match.group(1)) 
        
    return fields
 
def create_HTML_list_from_list(data_list, intro = '') -> str:
    """
    Genera una lista HMTL a partir de un list 
    """ 
    html_list = ''

    html_list = f'<p style="padding-left: 3rem">{intro}</p><ul style="margin-left: 3rem">'
    for mf in data_list:
      html_list += f'<li>{mf}'  
    html_list += '</ul>'

    return html_list

