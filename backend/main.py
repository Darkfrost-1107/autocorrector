#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.corrector import Corrector

"""
Aplicación web para corrección ortográfica que utiliza Flask y la biblioteca autocorrect.
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
        
        return jsonify({
            "texto_original": texto_original,
            "texto_corregido": texto_corregido
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
            "tiempo_transcurrido": metricas.get("tiempo_transcurrido")
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
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        textarea {
            width: 100%;
            height: 200px;
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
    </style>
</head>
<body>
    <h1>Corrector Ortográfico</h1>
    
    <div>
        <h3>Texto original:</h3>
        <textarea id="texto-original" placeholder="Ingrese el texto que desea corregir..."></textarea>
    </div>
    
    <div>
        <button id="corregir">Corregir texto</button>
        <button id="corregir-con-tiempo">Corregir y medir tiempo</button>
    </div>
    
    <div class="result" id="result">
        <h3>Texto corregido:</h3>
        <div id="texto-corregido"></div>
        <div class="stats" id="stats"></div>
    </div>

    <script>
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
                document.getElementById('stats').textContent = '';
                document.getElementById('result').style.display = 'block';
                
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
                document.getElementById('stats').textContent = `Tiempo de corrección: ${data.tiempo_transcurrido.toFixed(5)} segundos`;
                document.getElementById('result').style.display = 'block';
                
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