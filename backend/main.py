#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.corrector import Corrector

"""
Aplicación web para corrección ortográfica que utiliza Flask y la biblioteca autocorrect.
Incluye funcionalidad para comparar textos con un texto de referencia.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Crear una instancia global del corrector
corrector = Corrector()

@app.route('/')
def index():
    """Ruta principal que muestra la página de inicio"""
    return render_template('index.html')

@app.route('/corregir', methods=['POST'])
def corregir():
    """
    Endpoint para corregir texto sin medir el tiempo
    """
    if request.method == 'POST':
        data = request.json
        texto_original = data.get('texto', '')
        
        if not texto_original:
            return jsonify({"error": "No se proporcionó texto para corregir"})
        
        texto_corregido = corrector.correct(texto_original)
        
        # Obtener las métricas de corrección
        corrector.init_measure()
        corrector.end_measure()
        metricas = corrector.metrics()
        
        return jsonify({
            "texto_original": texto_original,
            "texto_corregido": texto_corregido,
            "palabras_corregidas": metricas.get("palabras_corregidas", 0),
            "total_palabras": metricas.get("total_palabras", 0),
            "porcentaje_correccion": metricas.get("porcentaje_correccion", 0),
            "detalle_correcciones": metricas.get("detalle_correcciones", [])
        })

@app.route('/corregir-con-tiempo', methods=['POST'])
def corregir_con_tiempo():
    """
    Endpoint para corregir texto midiendo el tiempo
    """
    if request.method == 'POST':
        data = request.json
        texto_original = data.get('texto', '')
        
        if not texto_original:
            return jsonify({"error": "No se proporcionó texto para corregir"})
        
        corrector.init_measure()
        texto_corregido = corrector.correct(texto_original)
        corrector.end_measure()
        
        metricas = corrector.metrics()
        
        return jsonify({
            "texto_original": texto_original,
            "texto_corregido": texto_corregido,
            "tiempo_transcurrido": metricas.get("tiempo_transcurrido"),
            "palabras_corregidas": metricas.get("palabras_corregidas", 0),
            "total_palabras": metricas.get("total_palabras", 0),
            "porcentaje_correccion": metricas.get("porcentaje_correccion", 0),
            "detalle_correcciones": metricas.get("detalle_correcciones", [])
        })

@app.route('/comparar', methods=['POST'])
def comparar():
    """
    Endpoint para comparar un texto con un texto de referencia
    """
    if request.method == 'POST':
        data = request.json
        texto_comparar = data.get('texto_comparar', '')
        texto_referencia = data.get('texto_referencia', '')
        
        if not texto_comparar:
            return jsonify({"error": "No se proporcionó texto para comparar"})
        
        if not texto_referencia:
            return jsonify({"error": "No se proporcionó texto de referencia"})
        
        # Establecer el texto de referencia
        corrector.set_reference_text(texto_referencia)
        
        # Realizar la comparación
        metricas_comparacion = corrector.compare_with_reference(texto_comparar)
        
        return jsonify({
            "texto_comparado": texto_comparar,
            "texto_referencia": texto_referencia,
            "metricas_comparacion": metricas_comparacion
        })

# Crear las plantillas HTML necesarias
@app.route('/crear_templates')
def crear_templates():
    """
    Esta ruta se usa solo para desarrollo y crea los archivos de plantillas necesarios.
    En un entorno de producción, estos archivos deberían existir físicamente.
    """
    import os
    
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Crear index.html
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corrector Ortográfico</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #f9f9f9;
            display: none;
        }
        .stats {
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }
        .correction-details {
            margin-top: 15px;
            border-top: 1px solid #ddd;
            padding-top: 15px;
        }
        .correction-item {
            margin-bottom: 5px;
            padding: 5px;
            background-color: #f0f0f0;
            border-radius: 3px;
        }
        .original-word {
            color: #e74c3c;
            text-decoration: line-through;
            margin-right: 10px;
        }
        .corrected-word {
            color: #2ecc71;
            font-weight: bold;
        }
        .comparison-details {
            margin-top: 15px;
            border-top: 1px solid #ddd;
            padding-top: 15px;
        }
        .comparison-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }
        .stat-item {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
        }
        .difference-item {
            margin-bottom: 5px;
            padding: 5px;
            background-color: #f0f0f0;
            border-radius: 3px;
        }
        .inserted-word {
            color: #2ecc71;
            font-weight: bold;
        }
        .deleted-word {
            color: #e74c3c;
            text-decoration: line-through;
        }
        .replaced-word-original {
            color: #e74c3c;
            text-decoration: line-through;
            margin-right: 10px;
        }
        .replaced-word-reference {
            color: #3498db;
            font-weight: bold;
        }
        .tab-container {
            margin-bottom: 20px;
        }
        .tab-buttons {
            display: flex;
            border-bottom: 1px solid #ccc;
        }
        .tab-button {
            padding: 10px 20px;
            cursor: pointer;
            background-color: #f1f1f1;
            border: none;
            outline: none;
            margin-right: 5px;
            border-radius: 5px 5px 0 0;
        }
        .tab-button.active {
            background-color: #4CAF50;
            color: white;
        }
        .tab-content {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 5px 5px;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <h1>Corrector Ortográfico y Comparador de Textos</h1>
    
    <div class="tab-container">
        <div class="tab-buttons">
            <button class="tab-button active" onclick="openTab(event, 'corrector-tab')">Corrector Ortográfico</button>
            <button class="tab-button" onclick="openTab(event, 'comparador-tab')">Comparador de Textos</button>
        </div>
        
        <div id="corrector-tab" class="tab-content active">
            <div>
                <h3>Texto original:</h3>
                <textarea id="texto-original" placeholder="Ingrese el texto que desea corregir..."></textarea>
            </div>
            
            <div>
                <button id="corregir">Corregir texto</button>
                <button id="corregir-con-tiempo">Corregir y medir tiempo</button>
            </div>
            
            <div class="result" id="result-corrector">
                <h3>Texto corregido:</h3>
                <div id="texto-corregido"></div>
                <div class="stats" id="stats-corrector"></div>
                <div class="correction-details" id="correction-details"></div>
            </div>
        </div>
        
        <div id="comparador-tab" class="tab-content">
            <div>
                <h3>Texto a comparar:</h3>
                <textarea id="texto-comparar" placeholder="Ingrese el texto que desea comparar..."></textarea>
            </div>
            
            <div>
                <h3>Texto de referencia (considerado correcto):</h3>
                <textarea id="texto-referencia" placeholder="Ingrese el texto de referencia..."></textarea>
            </div>
            
            <div>
                <button id="comparar">Comparar textos</button>
            </div>
            
            <div class="result" id="result-comparador">
                <h3>Resultados de la comparación:</h3>
                <div class="stats" id="stats-comparador"></div>
                <div class="comparison-stats" id="comparison-stats"></div>
                <div class="comparison-details" id="comparison-details"></div>
            </div>
        </div>
    </div>

    <script>
        // Funciones para las pestañas
        function openTab(evt, tabName) {
            var i, tabContent, tabButtons;
            
            tabContent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabContent.length; i++) {
                tabContent[i].classList.remove("active");
            }
            
            tabButtons = document.getElementsByClassName("tab-button");
            for (i = 0; i < tabButtons.length; i++) {
                tabButtons[i].classList.remove("active");
            }
            
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
        
        // Funciones para el corrector
        document.getElementById('corregir').addEventListener('click', async function() {
            const textoOriginal = document.getElementById('texto-original').value;
            
            if (!textoOriginal.trim()) {
                alert('Por favor, ingrese un texto para corregir.');
                return;
            }
            
            try {
                const response = await fetch('/corregir', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ texto: textoOriginal }),
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                document.getElementById('texto-corregido').textContent = data.texto_corregido;
                
                // Mostrar estadísticas de corrección
                const statsText = `Palabras corregidas: ${data.palabras_corregidas} de ${data.total_palabras} (${data.porcentaje_correccion.toFixed(2)}%)`;
                document.getElementById('stats-corrector').textContent = statsText;
                
                // Mostrar detalles de correcciones
                const correctionDetailsDiv = document.getElementById('correction-details');
                correctionDetailsDiv.innerHTML = '';
                
                if (data.detalle_correcciones && data.detalle_correcciones.length > 0) {
                    const headerElement = document.createElement('h4');
                    headerElement.textContent = 'Detalle de correcciones:';
                    correctionDetailsDiv.appendChild(headerElement);
                    
                    data.detalle_correcciones.forEach(correction => {
                        const correctionItem = document.createElement('div');
                        correctionItem.className = 'correction-item';
                        
                        const originalSpan = document.createElement('span');
                        originalSpan.className = 'original-word';
                        originalSpan.textContent = correction.original;
                        
                        const arrowSpan = document.createElement('span');
                        arrowSpan.textContent = ' → ';
                        
                        const correctedSpan = document.createElement('span');
                        correctedSpan.className = 'corrected-word';
                        correctedSpan.textContent = correction.corregido;
                        
                        correctionItem.appendChild(originalSpan);
                        correctionItem.appendChild(arrowSpan);
                        correctionItem.appendChild(correctedSpan);
                        
                        correctionDetailsDiv.appendChild(correctionItem);
                    });
                }
                
                document.getElementById('result-corrector').style.display = 'block';
                
            } catch (error) {
                console.error('Error:', error);
                alert('Ha ocurrido un error al procesar su solicitud.');
            }
        });
        
        document.getElementById('corregir-con-tiempo').addEventListener('click', async function() {
            const textoOriginal = document.getElementById('texto-original').value;
            
            if (!textoOriginal.trim()) {
                alert('Por favor, ingrese un texto para corregir.');
                return;
            }
            
            try {
                const response = await fetch('/corregir-con-tiempo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ texto: textoOriginal }),
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                document.getElementById('texto-corregido').textContent = data.texto_corregido;
                
                // Mostrar estadísticas de corrección y tiempo
                const statsText = `Tiempo de corrección: ${data.tiempo_transcurrido.toFixed(5)} segundos | Palabras corregidas: ${data.palabras_corregidas} de ${data.total_palabras} (${data.porcentaje_correccion.toFixed(2)}%)`;
                document.getElementById('stats-corrector').textContent = statsText;
                
                // Mostrar detalles de correcciones
                const correctionDetailsDiv = document.getElementById('correction-details');
                correctionDetailsDiv.innerHTML = '';
                
                if (data.detalle_correcciones && data.detalle_correcciones.length > 0) {
                    const headerElement = document.createElement('h4');
                    headerElement.textContent = 'Detalle de correcciones:';
                    correctionDetailsDiv.appendChild(headerElement);
                    
                    data.detalle_correcciones.forEach(correction => {
                        const correctionItem = document.createElement('div');
                        correctionItem.className = 'correction-item';
                        
                        const originalSpan = document.createElement('span');
                        originalSpan.className = 'original-word';
                        originalSpan.textContent = correction.original;
                        
                        const arrowSpan = document.createElement('span');
                        arrowSpan.textContent = ' → ';
                        
                        const correctedSpan = document.createElement('span');
                        correctedSpan.className = 'corrected-word';
                        correctedSpan.textContent = correction.corregido;
                        
                        correctionItem.appendChild(originalSpan);
                        correctionItem.appendChild(arrowSpan);
                        correctionItem.appendChild(correctedSpan);
                        
                        correctionDetailsDiv.appendChild(correctionItem);
                    });
                }
                
                document.getElementById('result-corrector').style.display = 'block';
                
            } catch (error) {
                console.error('Error:', error);
                alert('Ha ocurrido un error al procesar su solicitud.');
            }
        });
        
        // Función para el comparador
        document.getElementById('comparar').addEventListener('click', async function() {
            const textoComparar = document.getElementById('texto-comparar').value;
            const textoReferencia = document.getElementById('texto-referencia').value;
            
            if (!textoComparar.trim()) {
                alert('Por favor, ingrese un texto para comparar.');
                return;
            }
            
            if (!textoReferencia.trim()) {
                alert('Por favor, ingrese un texto de referencia.');
                return;
            }
            
            try {
                const response = await fetch('/comparar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        texto_comparar: textoComparar,
                        texto_referencia: textoReferencia
                    }),
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                const metrics = data.metricas_comparacion;
                
                // Mostrar resumen de comparación
                document.getElementById('stats-comparador').textContent = `Similitud: ${(metrics.ratio_similitud * 100).toFixed(2)}% | F1 Score: ${(metrics.f1_score * 100).toFixed(2)}% | Tasa de error: ${(metrics.tasa_error_palabras * 100).toFixed(2)}%`;
                
                // Mostrar estadísticas detalladas
                const statsDiv = document.getElementById('comparison-stats');
                statsDiv.innerHTML = '';
                
                // Añadir estadísticas principales
                const statsItems = [
                    { label: "Total palabras (texto a comparar)", value: metrics.total_palabras_comparado },
                    { label: "Total palabras (texto de referencia)", value: metrics.total_palabras_referencia },
                    { label: "Palabras coincidentes", value: metrics.palabras_coincidentes },
                    { label: "Palabras faltantes (a insertar)", value: metrics.palabras_insertadas },
                    { label: "Palabras sobrantes (a eliminar)", value: metrics.palabras_eliminadas },
                    { label: "Palabras a reemplazar", value: metrics.palabras_reemplazadas },
                    { label: "Precisión", value: `${(metrics.precision * 100).toFixed(2)}%` },
                    { label: "Recall (Exhaustividad)", value: `${(metrics.recall * 100).toFixed(2)}%` }
                ];
                
                statsItems.forEach(item => {
                    const statElement = document.createElement('div');
                    statElement.className = 'stat-item';
                    statElement.textContent = `${item.label}: ${item.value}`;
                    statsDiv.appendChild(statElement);
                });
                
                // Mostrar detalles de las diferencias
                const comparisonDetailsDiv = document.getElementById('comparison-details');
                comparisonDetailsDiv.innerHTML = '';
                
                if (metrics.detalles_diferencias && metrics.detalles_diferencias.length > 0) {
                    const headerElement = document.createElement('h4');
                    headerElement.textContent = 'Detalle de diferencias:';
                    comparisonDetailsDiv.appendChild(headerElement);
                    
                    metrics.detalles_diferencias.forEach(difference => {
                        const diffItem = document.createElement('div');
                        diffItem.className = 'difference-item';
                        
                        if (difference.tipo === 'reemplazo') {
                            const originalSpan = document.createElement('span');
                            originalSpan.className = 'replaced-word-original';
                            originalSpan.textContent = difference.texto_comparado;
                            
                            const arrowSpan = document.createElement('span');
                            arrowSpan.textContent = ' → ';
                            
                            const referenceSpan = document.createElement('span');
                            referenceSpan.className = 'replaced-word-reference';
                            referenceSpan.textContent = difference.texto_referencia;
                            
                            diffItem.appendChild(originalSpan);
                            diffItem.appendChild(arrowSpan);
                            diffItem.appendChild(referenceSpan);
                            diffItem.appendChild(document.createTextNode(' (reemplazo)'));
                        } 
                        else if (difference.tipo === 'eliminación') {
                            const deletedSpan = document.createElement('span');
                            deletedSpan.className = 'deleted-word';
                            deletedSpan.textContent = difference.texto_comparado;
                            
                            diffItem.appendChild(deletedSpan);
                            diffItem.appendChild(document.createTextNode(' (eliminar)'));
                        }
                        else if (difference.tipo === 'inserción') {
                            const insertedSpan = document.createElement('span');
                            insertedSpan.className = 'inserted-word';
                            insertedSpan.textContent = difference.texto_referencia;
                            
                            diffItem.appendChild(document.createTextNode('Falta: '));
                            diffItem.appendChild(insertedSpan);
                            diffItem.appendChild(document.createTextNode(' (insertar)'));
                        }
                        
                        comparisonDetailsDiv.appendChild(diffItem);
                    });
                }
                
                document.getElementById('result-comparador').style.display = 'block';
                
            } catch (error) {
                console.error('Error:', error);
                alert('Ha ocurrido un error al procesar su solicitud.');
            }
        });
    </script>
</body>
</html>""")
    
    return "Plantillas creadas correctamente"

if __name__ == '__main__':
    # Crear las plantillas si no existen
    import os
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    if not os.path.exists(templates_dir) or not os.path.exists(os.path.join(templates_dir, 'index.html')):
        app.test_client().get('/crear_templates')
    
    # Iniciar la aplicación Flask
    app.run(debug=True)