# Instrucciones de Instalación y Uso
Requisitos previos

Python 3.7 o superior
pip (gestor de paquetes de Python)
Acceso a la terminal/línea de comandos

Paso 1: Descargar el código
Descarga todos los archivos del proyecto a un directorio en tu computadora.

Paso 2: Configurar el entorno virtual (recomendado)
Es recomendable usar un entorno virtual para aislar las dependencias:
bash# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
## En Windows:
venv\Scripts\activate
## En macOS/Linux:
source venv/bin/activate

Paso 3: Instalar dependencias
Instala todas las dependencias del proyecto usando el archivo requirements.txt:
bashpip install -r requirements.txt

Paso 4: Descargar datos adicionales de NLTK
Necesitarás descargar el corpus en español para NLTK:

> python -c "import nltk; nltk.download('cess_esp')"

Paso 5: Ejecutar la aplicación
Ejecuta la aplicación Flask:
> python app.py

La aplicación estará disponible en: http://127.0.0.1:5000/

# Uso de la aplicación

## Corrector ortográfico:

Ingresa el texto a corregir en el campo de texto
Haz clic en "Corregir texto" o "Corregir y medir tiempo"
Verás el texto corregido, estadísticas y detalles de las correcciones


## Comparador de textos:

Ingresa un texto para comparar
Ingresa un texto de referencia (considerado correcto)
Haz clic en "Comparar textos"
Verás estadísticas de similitud, precisión, recall y F1 score



## Configuración avanzada
Puedes modificar la configuración del corrector en el código:
pythonfrom lib.corrector import CorrectorAvanzado

# Crear un corrector con configuración personalizada
corrector = CorrectorAvanzado(
    lang='es',          # Idioma ('es' para español)
    threshold=5,        # Umbral de frecuencia mínima
    fast=False,         # Modo rápido (menos preciso)
    only_replacements=False  # Solo hacer reemplazos
)

# Solución de problemas

Error con el corpus NLTK: Si encuentras problemas con el corpus en español, asegúrate de haberlo descargado correctamente.

Problemas con Flask: Verifica que estés usando la versión correcta de Flask y sus dependencias.

Rendimiento lento: Si el corrector es lento con textos grandes, prueba activando el modo fast=True.