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
        self.original_text = None
        self.corrected_text = None
        self.correction_count = 0
    
    def correct(self, text):
        """
        Corrige la ortografía del texto dado utilizando la biblioteca autocorrect.

        Args:
            text (str): El texto a corregir.

        Returns:
            str: El texto corregido.
        """
        self.original_text = text
        self.corrected_text = spell(text)
        
        # Contar las correcciones realizadas
        original_words = self.original_text.split()
        corrected_words = self.corrected_text.split()
        
        # Asegurar que ambas listas tengan la misma longitud
        min_length = min(len(original_words), len(corrected_words))
        self.correction_count = sum(1 for i in range(min_length) if original_words[i] != corrected_words[i])
        
        return self.corrected_text
    
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
        
        if self.original_text is None:
            return {
                "tiempo_transcurrido": self.measure, 
                "segundos": self.measure,
                "error": "No hay texto original. Ejecute correct() primero."
            }
        
        # Calcular el porcentaje de palabras corregidas
        total_words = len(self.original_text.split())
        correction_percentage = (self.correction_count / total_words * 100) if total_words > 0 else 0
        
        # Identificar las palabras que fueron corregidas
        original_words = self.original_text.split()
        corrected_words = self.corrected_text.split()
        min_length = min(len(original_words), len(corrected_words))
        
        corrected_pairs = []
        for i in range(min_length):
            if original_words[i] != corrected_words[i]:
                corrected_pairs.append({
                    "original": original_words[i],
                    "corregido": corrected_words[i]
                })
        
        return {
            "tiempo_transcurrido": self.measure, 
            "segundos": self.measure,
            "texto_original": self.original_text,
            "texto_corregido": self.corrected_text,
            "total_palabras": total_words,
            "palabras_corregidas": self.correction_count,
            "porcentaje_correccion": correction_percentage,
            "detalle_correcciones": corrected_pairs
        }