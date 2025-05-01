#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para corrección ortográfica que utiliza la biblioteca autocorrect.
Incluye funcionalidad para comparar un texto con un texto de referencia correcto.
"""

from autocorrect import Speller
from collections import Counter
import time
import difflib
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
        self.reference_text = None
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
    
    def set_reference_text(self, reference_text):
        """
        Establece un texto de referencia considerado como correcto para comparar.

        Args:
            reference_text (str): El texto de referencia correcto.

        Returns:
            bool: True si se estableció correctamente, False en caso contrario.
        """
        if not reference_text or not isinstance(reference_text, str):
            return False
        
        self.reference_text = reference_text
        return True
    
    def compare_with_reference(self, text_to_compare=None):
        """
        Compara un texto con el texto de referencia establecido.
        Si no se proporciona texto_to_compare, se usa el texto corregido.

        Args:
            text_to_compare (str, optional): El texto a comparar con la referencia.

        Returns:
            dict: Diccionario con métricas de comparación.
        """
        if not self.reference_text:
            return {"error": "No hay texto de referencia establecido. Use set_reference_text primero."}
        
        # Si no se proporciona texto a comparar, usar el texto corregido o el original
        text_to_compare = text_to_compare or self.corrected_text or self.original_text
        
        if not text_to_compare:
            return {"error": "No hay texto para comparar. Proporcione un texto o use correct() primero."}
        
        # Convertir textos a listas de palabras
        reference_words = self.reference_text.split()
        compare_words = text_to_compare.split()
        
        # Usar difflib para obtener la secuencia de operaciones para transformar text_to_compare en reference_text
        matcher = difflib.SequenceMatcher(None, compare_words, reference_words)
        opcodes = matcher.get_opcodes()
        
        # Contar diferentes tipos de diferencias
        matches = sum(1 for tag, i1, i2, j1, j2 in opcodes if tag == 'equal')
        inserts = sum(j2 - j1 for tag, i1, i2, j1, j2 in opcodes if tag == 'insert')
        deletes = sum(i2 - i1 for tag, i1, i2, j1, j2 in opcodes if tag == 'delete')
        replaces = sum(min(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in opcodes if tag == 'replace')
        
        total_reference_words = len(reference_words)
        total_compare_words = len(compare_words)
        
        # Calcular similitud según Levenshtein (1 - distancia/longitud)
        similarity_ratio = matcher.ratio()
        
        # Calcular precisión, recall y F1 score
        precision = matches / total_compare_words if total_compare_words > 0 else 0
        recall = matches / total_reference_words if total_reference_words > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calcular error rate
        word_error_rate = (inserts + deletes + replaces) / total_reference_words if total_reference_words > 0 else 0
        
        # Recolectar detalles de diferencias
        difference_details = []
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'replace':
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    if i < len(compare_words) and j < len(reference_words):
                        difference_details.append({
                            "tipo": "reemplazo",
                            "texto_comparado": compare_words[i],
                            "texto_referencia": reference_words[j]
                        })
            elif tag == 'delete':
                for i in range(i1, i2):
                    if i < len(compare_words):
                        difference_details.append({
                            "tipo": "eliminación",
                            "texto_comparado": compare_words[i],
                            "texto_referencia": None
                        })
            elif tag == 'insert':
                for j in range(j1, j2):
                    if j < len(reference_words):
                        difference_details.append({
                            "tipo": "inserción",
                            "texto_comparado": None,
                            "texto_referencia": reference_words[j]
                        })
        
        return {
            "total_palabras_referencia": total_reference_words,
            "total_palabras_comparado": total_compare_words,
            "palabras_coincidentes": matches,
            "palabras_insertadas": inserts,
            "palabras_eliminadas": deletes,
            "palabras_reemplazadas": replaces,
            "ratio_similitud": similarity_ratio,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "tasa_error_palabras": word_error_rate,
            "detalles_diferencias": difference_details
        }
    
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
        
        result = {
            "tiempo_transcurrido": self.measure, 
            "segundos": self.measure,
            "texto_original": self.original_text,
            "texto_corregido": self.corrected_text,
            "total_palabras": total_words,
            "palabras_corregidas": self.correction_count,
            "porcentaje_correccion": correction_percentage,
            "detalle_correcciones": corrected_pairs
        }
        
        # Si hay un texto de referencia, agregar métricas de comparación
        if self.reference_text:
            comparison_metrics = self.compare_with_reference()
            if "error" not in comparison_metrics:
                result["comparacion_referencia"] = comparison_metrics
        
        return result