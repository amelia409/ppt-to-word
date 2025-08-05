from flask import Flask, request, jsonify
from ppt_processor import extract_text_from_pptx
from ai_writer import generate_explanation
from word_generator import create_word_document
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "API funcionando",
        "endpoints": {
            "procesar_pptx": "POST /process"
        }
    })

@app.route('/process', methods=['POST'])
def process_pptx():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió archivo"}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.pptx'):
        return jsonify({"error": "Archivo PPTX inválido"}), 400
    
    # Guardar archivo temporal
    temp_path = os.path.join("assets", file.filename)
    file.save(temp_path)
    
    try:
        # 1. Extraer texto
        text = extract_text_from_pptx(temp_path)
        
        # 2. Generar explicación con IA
        explanation = generate_explanation(text)
        
        # 3. Crear documento Word
        output_path = os.path.join("assets", "output.docx")
        create_word_document(explanation, output_path)
        
        return jsonify({
            "status": "success",
            "text_extracted": text[:200] + "...",  # Preview
            "word_file": output_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs("assets", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)