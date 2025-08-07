import google.generativeai as genai
import os
import re

def clean_extracted_text(text: str) -> str:
    """Limpia y normaliza texto extraído - MEJORADO según feedback"""
    # Eliminar caracteres especiales y normalizar espacios
    text = re.sub(r'\s+', ' ', text)  # Múltiples espacios a uno
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Múltiples saltos de línea
    text = text.strip()
    
    # Eliminar fragmentos irrelevantes y muy cortos
    lines = text.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        # Filtrar líneas muy cortas o irrelevantes
        if len(line) < 15:
            continue
        # Filtrar contenido genérico común de presentaciones
        if any(generic in line.lower() for generic in [
            "slide", "página", "click aquí", "siguiente", "anterior", 
            "fondo", "plantilla", "diseño", "menú", "navegación"
        ]):
            continue
        clean_lines.append(line)
    
    return '\n'.join(clean_lines)

def generate_explanation(content: str) -> str:
    """Genera explicación mejorada con formato usando Gemini"""
    # Configurar Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Limpiar contenido primero
    clean_content = clean_extracted_text(content)
    
    prompt = f"""Eres un experto en crear material didáctico académico de alta calidad en ESPAÑOL.

CONTENIDO A PROCESAR:
{clean_content}

INSTRUCCIONES CRÍTICAS PARA EXCELENCIA ACADÉMICA:

📋 ESTRUCTURA JERÁRQUICA OBLIGATORIA:
- ## para títulos principales temáticos (NO por slide, sino por tema)
- ### para subtemas lógicos  
- #### para conceptos específicos
- Reorganiza el contenido lógicamente, ignorando el orden original de slides
- Crea una narrativa académica coherente y progresiva

🚫 ELIMINAR ABSOLUTAMENTE:
- Repeticiones de conceptos básicos ya explicados
- Frases genéricas sin valor específico del contenido
- Texto de relleno o artificialmente alargado
- Contenido fuera del material fuente
- Explicaciones superficiales

💻 CÓDIGO (obligatorio si aparece):
- Explica línea por línea el funcionamiento
- Comenta el propósito en el contexto académico
- No asumas conocimientos previos no justificados
- Incluye comentarios explicativos en español

� ENRIQUECIMIENTO PEDAGÓGICO:
- Tablas comparativas para listas complejas
- Viñetas (•) para conceptos clave
- Resúmenes al final de secciones importantes
- Ejercicios prácticos relevantes al contenido
- Preguntas de reflexión para consolidar aprendizaje

✅ CALIDAD ACADÉMICA:
- Mínimo 200 palabras por sección principal (sin relleno)
- Profundidad real basada únicamente en el material fuente
- Español formal pero didáctico
- Estructura lógica que facilite el aprendizaje progresivo
- Transiciones fluidas entre conceptos

🎯 OBJETIVO: Documento profesional, pedagógicamente sólido y realmente útil para el aprendizaje."""
- Progresión lógica de conceptos simples a complejos
- Cada párrafo debe aportar valor educativo específico

❌ PROHIBIDO ESTRICTAMENTE:
- Contenido genérico no relacionado con el archivo fuente
- Repeticiones de conceptos ya cubiertos
- Frases de relleno sin valor específico
- Explicaciones superficiales de código
- Desviarse del material original

FORMATO DE SALIDA REQUERIDO:
- Documento completamente en español
- Estructura clara con títulos jerárquicos
- Contenido pedagógicamente organizado
- Sin repeticiones innecesarias
- Enfoque en la comprensión profunda del material específico

Genera un documento que sea una referencia académica útil, completa y pedagógicamente sólida basada ÚNICAMENTE en el contenido proporcionado."""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Más conservador para contenido académico
                max_output_tokens=2048,
                top_p=0.9
            )
        )
        return response.text
    except Exception as e:
        # Fallback en caso de error
        return f"Error generando contenido con IA: {str(e)}\n\nContenido original:\n{clean_content}"