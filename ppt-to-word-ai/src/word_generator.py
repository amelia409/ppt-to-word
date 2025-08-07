from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
from PIL import Image
import os
from .ai_writer import generate_explanation

def create_word_document(content: list, original_filename: str) -> str:
    """Crea documento Word académico mejorado según feedback del usuario"""
    doc = Document()
    
    # Configuración de estilos mejorada
    styles = doc.styles
    font = styles['Normal'].font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Portada académica profesional
    doc.add_heading(f"Documento Académico", 0)
    doc.add_paragraph(f"Material didáctico basado en: {original_filename}")
    doc.add_paragraph("Procesado con inteligencia artificial para fines pedagógicos")
    doc.add_paragraph("Contenido estructurado y enriquecido para el aprendizaje\n")
    
    # Procesar cada slide/página CON MEJORAS CRÍTICAS
    for item in content:
        # Recopilar todo el texto relevante
        all_text = []
        
        # Agregar título si existe
        if item.get('title'):
            all_text.append(f"TÍTULO: {item['title']}")
        
        # Agregar contenido de texto
        for element in item["content"]:
            if element["type"] == "text" and len(element["data"].strip()) > 15:  # Filtrar texto muy corto
                all_text.append(element["data"])
        
        # Filtrar y agregar texto de imágenes solo si es significativo
        for img in item.get("images", []):
            if img.get("text") and len(img.get("text", "").strip()) > 25:  # Solo texto sustancial
                img_text = img.get("text", "").strip()
                # Filtrar contenido irrelevante de imágenes
                irrelevant_terms = ["slide", "página", "fondo", "plantilla", "diseño", "click", "aquí"]
                if not any(term in img_text.lower() for term in irrelevant_terms):
                    all_text.append(f"CONTENIDO DE IMAGEN: {img_text}")
        
        # Combinar todo el contenido
        combined_content = "\n".join(all_text)
        
        if combined_content.strip():
            # USAR IA MEJORADA OBLIGATORIAMENTE
            try:
                enhanced_content = generate_explanation(combined_content)
                
                # Procesar el contenido mejorado con estructura jerárquica
                lines = enhanced_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:  # Saltar líneas vacías
                        continue
                        
                    if line.startswith('##'):
                        # Título principal
                        doc.add_heading(line[2:].strip(), level=1)
                    elif line.startswith('###'):
                        # Subtítulo
                        doc.add_heading(line[3:].strip(), level=2)
                    elif line.startswith('####'):
                        # Sub-subtítulo
                        doc.add_heading(line[4:].strip(), level=3)
                    elif line.startswith('•') or line.startswith('- ') or line.startswith('* '):
                        # Lista con viñetas - mejorada
                        bullet_text = line[1:].strip() if line.startswith('•') else line[2:].strip()
                        para = doc.add_paragraph(bullet_text, style='List Bullet')
                    elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                        # Lista numerada
                        num_text = line[3:].strip()
                        para = doc.add_paragraph(num_text, style='List Number')
                    elif '```' in line:
                        # Código - se omite la línea de marcador pero se procesa el contenido
                        continue
                    elif line.startswith('**') and line.endswith('**'):
                        # Texto en negrita como párrafo destacado
                        para = doc.add_paragraph()
                        run = para.add_run(line[2:-2])
                        run.bold = True
                    elif len(line) > 10:  # Solo párrafos con contenido sustancial
                        # Párrafo normal
                        doc.add_paragraph(line)
                
            except Exception as e:
                # En caso de error con IA, documentar el problema
                doc.add_heading(f"Error procesando contenido con IA", level=1)
                doc.add_paragraph(f"Error: {str(e)}")
                doc.add_paragraph("Contenido original sin procesar:")
                doc.add_paragraph(combined_content)
        
        # SEPARADOR MEJORADO entre secciones (solo si hay contenido)
        if combined_content.strip():
            doc.add_paragraph()  # Espacio en blanco limpio
    
    # Guardar archivo con nomenclatura mejorada
    output_dir = "/app/assets/output"
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.splitext(original_filename)[0]
    output_filename = f"academic_{base_name}.docx"  # Cambio de prefijo
    output_path = os.path.join(output_dir, output_filename)
    
    doc.save(output_path)
    return output_path
