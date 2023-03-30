# -*- coding: utf-8 -*-

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