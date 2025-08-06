from flask import Flask, request, jsonify, send_file
from src.ppt_processor import extract_structured_content
from src.pdf_processor import extract_text_from_pdf
from src.ai_writer import generate_explanation
from src.word_generator import create_word_document
import os

app = Flask(__name__)

# Configuración de rutas absolutas para Docker
BASE_DIR = "/app"
INPUT_DIR = os.path.join(BASE_DIR, "assets", "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "output")

@app.route('/')
def home():
    return jsonify({
        "status": "API funcionando",
        "endpoints": {
            "procesar_archivo": "POST /process",
            "descargar": "GET /download/<filename>"
        }
    })

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo inválido"}), 400
    
    # Validar extensión
    valid_extensions = ('.pptx', '.ppt', '.pdf')
    if not file.filename.lower().endswith(valid_extensions):
        return jsonify({"error": "Solo se aceptan PPT, PPTX o PDF"}), 400
    
    # Crear directorios (ahora con rutas absolutas)
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    temp_path = os.path.join(INPUT_DIR, file.filename)
    file.save(temp_path)
    
    try:
        # Procesamiento según tipo
        if file.filename.lower().endswith('.pdf'):
            content = extract_text_from_pdf(temp_path)
        else:
            content = extract_structured_content(temp_path)
        
        # Generar Word
        output_path = create_word_document(content, file.filename)
        
        return jsonify({
            "status": "success",
            "download_url": f"/download/{os.path.basename(output_path)}",
            "filename": os.path.basename(output_path)
        })
    
    except Exception as e:
        app.logger.error(f"Error en procesamiento: {str(e)}")
        return jsonify({
            "error": "Error procesando archivo",
            "details": str(e)
        }), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    app.logger.error(f"Archivo no encontrado: {file_path}")
    return jsonify({"error": "Archivo no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)