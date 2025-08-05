from docx import Document
from docx.shared import Pt

def create_word_document(content: str, output_path: str) -> None:
    """
    Crea un documento Word con formato básico
    
    Args:
        content: Texto a incluir
        output_path: Ruta de salida (.docx)
    """
    doc = Document()
    
    # Configuración de estilo
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Añadir contenido
    for paragraph in content.split('\n'):
        if paragraph.strip():
            doc.add_paragraph(paragraph)
    
    doc.save(output_path)