#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación web para corrección ortográfica que utiliza Flask y la biblioteca autocorrect.
"""

from autocorrect import Speller
from collections import Counter
import time
from nltk.corpus import cess_esp 

words = cess_esp.words()

# Contar la frecuencia de cada palabra
word_freq = Counter(words)

# Convertir a un diccionario
word_freq_dict = dict(word_freq)

# Inicializar el corrector para español
spell = Speller(lang='es', nlp_data=word_freq_dict)

class Corrector:
    def __init__(self):
        self.init_time = None
        self.end_time = None
        self.measure = None
    
    def correct(self, text):
        """
        Corrige la ortografía del texto dado utilizando la biblioteca autocorrect.

        Args:
            text (str): El texto a corregir.

        Returns:
            str: El texto corregido.
        """
        return spell(text)
    
    def init_measure(self):
        """
        Inicializa la medición para el corrector.

        Returns:
            str: Un mensaje indicando que la medición ha sido inicializada.
        """
        self.init_time = time.time()
        self.end_time = None
        self.measure = None
        return "Medición inicializada"
    
    def end_measure(self):
        """
        Finaliza la medición para el corrector.

        Returns:
            str: Un mensaje indicando que la medición ha finalizado.
        """
        self.end_time = time.time()
        self.measure = self.end_time - self.init_time
        return "Medición finalizada"
    
    def metrics(self):
        """
        Devuelve las métricas para el corrector.

        Returns:
            dict: Un diccionario con las métricas del corrector.
        """
        if self.measure is None:
            return {"error": "No hay medición disponible. Ejecute init_measure() y end_measure() primero."}
        
        return {"tiempo_transcurrido": self.measure, "segundos": self.measure}

