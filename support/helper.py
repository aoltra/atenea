# -*- coding: utf-8 -*-

def is_set(value, option):
    """
    Devuelve True o False si la opción aparece en el valor
    Por ejemplo: is_set(25, 1) -> True
    Por ejemplo: is_set(25, 2) -> False
    """
    return value & 1 << option != 0