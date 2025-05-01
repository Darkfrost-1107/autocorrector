#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para corrección ortográfica que utiliza la biblioteca autocorrect con funcionalidades mejoradas.
Incluye opciones de configuración avanzadas y métricas detalladas.
"""

from autocorrect import Speller
from autocorrect import Word
from autocorrect.constants import alphabets
from collections import Counter
import time
import difflib
import re
from itertools import chain
from nltk.corpus import cess_esp 

# Cargar el corpus en español
words = cess_esp.words()

# Contar la frecuencia de cada palabra
word_freq = Counter(words)

# Convertir a un diccionario
word_freq_dict = dict(word_freq)

class CorrectorAvanzado:
    def __init__(self, lang='es', threshold=0, fast=False, only_replacements=False):
        """
        Inicializa el corrector con opciones avanzadas.
        
        Args:
            lang (str): Idioma para la corrección ('es' para español, 'en' para inglés, etc.)
            threshold (int): Umbral de frecuencia mínima para considerar palabras válidas
            fast (bool): Si es True, solo busca errores simples (más rápido pero menos preciso)
            only_replacements (bool): Si es True, solo realiza reemplazos (no agrega/elimina letras)
        """
        self.init_time = None
        self.end_time = None
        self.measure = None
        self.original_text = None
        self.corrected_text = None
        self.reference_text = None
        self.correction_count = 0
        
        # Parámetros de configuración del Speller
        self.lang = lang
        self.threshold = threshold
        self.fast = fast
        self.only_replacements = only_replacements
        
        # Inicializar el corrector con las opciones específicas
        self.spell = Speller(
            lang=lang, 
            threshold=threshold, 
            nlp_data=word_freq_dict,
            fast=fast,
            only_replacements=only_replacements
        )
        
        # Estadísticas del corrector
        self.stats = {
            'total_correcciones': 0,
            'correcciones_por_tipo': {
                'typos': 0,       # Errores simples (una letra)
                'double_typos': 0 # Errores dobles (dos letras)
            },
            'palabras_procesadas': 0
        }
    
    def update_config(self, **kwargs):
        """
        Actualiza la configuración del corrector.
        
        Args:
            **kwargs: Parámetros de configuración a actualizar
                - lang: Idioma para la corrección
                - threshold: Umbral de frecuencia
                - fast: Modo rápido
                - only_replacements: Solo reemplazos
        
        Returns:
            dict: La configuración actualizada
        """
        # Actualizar atributos
        for key, value in kwargs.items():
            if hasattr(self, key) and key in ['lang', 'threshold', 'fast', 'only_replacements']:
                setattr(self, key, value)
        
        # Reinicializar el speller con la nueva configuración
        self.spell = Speller(
            lang=self.lang, 
            threshold=self.threshold, 
            nlp_data=word_freq_dict,
            fast=self.fast,
            only_replacements=self.only_replacements
        )
        
        return {
            'lang': self.lang,
            'threshold': self.threshold,
            'fast': self.fast,
            'only_replacements': self.only_replacements
        }
    
    def get_correction_details(self, word):
        """
        Obtiene detalles sobre la corrección de una palabra.
        
        Args:
            word (str): Palabra a corregir
        
        Returns:
            dict: Detalles de la corrección
        """
        if word == "":
            return {"original": "", "corregido": "", "tipo": "no_correccion", "candidatos": []}
            
        # Obtener candidatos
        candidates = self.spell.get_candidates(word)
        candidates_sorted = sorted(candidates, key=lambda x: x[0], reverse=True)
        
        # Determinar el tipo de corrección
        correction_type = "no_correccion"
        if word in self.spell.nlp_data:
            correction_type = "no_correccion"  # Palabra correcta
        else:
            # Comprobar si es un typo simple
            w = Word(word, self.lang, self.only_replacements)
            typos = w.typos()
            if any(typo in self.spell.nlp_data for typo in typos):
                correction_type = "typo_simple"
                self.stats['correcciones_por_tipo']['typos'] += 1
            else:
                # Comprobar si es un typo doble
                if not self.fast:
                    double_typos = w.double_typos()
                    if any(typo in self.spell.nlp_data for typo in double_typos):
                        correction_type = "typo_doble"
                        self.stats['correcciones_por_tipo']['double_typos'] += 1
        
        # Obtener la mejor corrección
        best_candidate = max(candidates)[1] if candidates else word
        
        # Preservar mayúsculas
        if word and word[0].isupper():
            best_candidate = best_candidate[0].upper() + best_candidate[1:]
            
        return {
            "original": word,
            "corregido": best_candidate,
            "tipo": correction_type,
            "candidatos": [{"palabra": c[1], "frecuencia": c[0]} for c in candidates_sorted[:5]]  # Top 5 candidatos
        }
    
    def correct(self, text):
        """
        Corrige la ortografía del texto dado utilizando la biblioteca autocorrect.

        Args:
            text (str): El texto a corregir.

        Returns:
            str: El texto corregido.
        """
        self.original_text = text
        self.stats['palabras_procesadas'] = len(text.split())
        
        # Reiniciar contadores de estadísticas
        self.stats['total_correcciones'] = 0
        self.stats['correcciones_por_tipo'] = {
            'typos': 0,
            'double_typos': 0
        }
        
        # Usar la función de corrección de autocorrect
        self.corrected_text = self.spell(text)
        
        # Recopilar información detallada sobre correcciones
        original_words = self.original_text.split()
        corrected_words = self.corrected_text.split()
        
        # Asegurar que ambas listas tengan la misma longitud
        min_length = min(len(original_words), len(corrected_words))
        
        # Analizar correcciones
        corrected_pairs = []
        for i in range(min_length):
            if original_words[i] != corrected_words[i]:
                # Obtener detalles de corrección
                correction_details = self.get_correction_details(original_words[i])
                corrected_pairs.append(correction_details)
                self.stats['total_correcciones'] += 1
        
        self.correction_count = self.stats['total_correcciones']
        
        return self.corrected_text
    
    def correct_word(self, word):
        """
        Corrige una sola palabra y proporciona información detallada.

        Args:
            word (str): La palabra a corregir.

        Returns:
            dict: Información detallada de la corrección.
        """
        correction_details = self.get_correction_details(word)
        if correction_details["original"] != correction_details["corregido"]:
            self.stats['total_correcciones'] += 1
        
        return correction_details
    
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
        Si no se proporciona text_to_compare, se usa el texto corregido.

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
                # Obtener detalles más completos sobre la corrección
                details = self.get_correction_details(original_words[i])
                corrected_pairs.append(details)
        
        result = {
            "tiempo_transcurrido": self.measure, 
            "segundos": self.measure,
            "texto_original": self.original_text,
            "texto_corregido": self.corrected_text,
            "total_palabras": total_words,
            "palabras_corregidas": self.correction_count,
            "porcentaje_correccion": correction_percentage,
            "detalle_correcciones": corrected_pairs,
            "estadisticas_corrector": {
                "total_correcciones": self.stats['total_correcciones'],
                "typos_simples": self.stats['correcciones_por_tipo']['typos'],
                "typos_dobles": self.stats['correcciones_por_tipo']['double_typos'],
                "velocidad_procesamiento": f"{(total_words / self.measure) if self.measure > 0 else 0:.2f} palabras/segundo",
                "configuracion_actual": {
                    "lang": self.lang,
                    "threshold": self.threshold,
                    "fast": self.fast,
                    "only_replacements": self.only_replacements
                }
            }
        }
        
        # Si hay un texto de referencia, agregar métricas de comparación
        if self.reference_text:
            comparison_metrics = self.compare_with_reference()
            if "error" not in comparison_metrics:
                result["comparacion_referencia"] = comparison_metrics
        
        return result

# Para mantener compatibilidad, también proveemos la clase Corrector original
class Corrector(CorrectorAvanzado):
    def __init__(self):
        super().__init__(lang='es', threshold=0, fast=False, only_replacements=False)