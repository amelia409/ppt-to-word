from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
from PIL import Image
import os

def create_word_document(content: list, original_filename: str) -> str:
    """Crea documento Word con estructura profesional"""
    doc = Document()
    
    # Configuración de estilos
    styles = doc.styles
    font = styles['Normal'].font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Portada
    doc.add_heading(f"Documento generado de: {original_filename}", 0)
    doc.add_paragraph("\n")
    
    # Contenido por slide/página
    for item in content:
        # Encabezado
        title = f"{'Slide' if 'slide_number' in item else 'Página'} {item.get('slide_number', item.get('page_number'))}"
        if item.get('title'):
            title += f": {item['title']}"
        doc.add_heading(title, level=1)
        
        # Texto
        for element in item["content"]:
            if element["type"] == "text":
                doc.add_paragraph(element["data"])
        
        # Imágenes
        for img in item.get("images", []):
            try:
                image_stream = io.BytesIO(img["image"])
                doc.add_picture(image_stream, width=Inches(4.5))
                if img.get("description") or img.get("text"):
                    caption = img.get("description", "") + " " + img.get("text", "")
                    doc.add_paragraph(caption.strip(), style="Caption")
            except Exception as e:
                print(f"Error insertando imagen: {e}")
        
        doc.add_page_break()
    
    # Corrección clave: Usar ruta absoluta consistente con Docker
    output_dir = "/app/assets/output"  # Ruta absoluta dentro del contenedor
    os.makedirs(output_dir, exist_ok=True)
    
    output_filename = os.path.join(
        output_dir,
        original_filename.replace('.pptx', '.docx')
                        .replace('.ppt', '.docx')
                        .replace('.pdf', '.docx')
    )
    
    doc.save(output_filename)
    return output_filename  # Devuelve ruta absoluta