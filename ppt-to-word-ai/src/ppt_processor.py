from pptx import Presentation
import pytesseract
from PIL import Image
import io

def extract_text_from_pptx(file_path: str) -> str:
    """
    Extrae texto de un archivo PPTX, incluyendo OCR para imágenes
    
    Args:
        file_path: Ruta al archivo .pptx
    
    Returns:
        Texto combinado de todas las slides
    """
    prs = Presentation(file_path)
    full_text = []
    
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                full_text.append(shape.text.strip())
            elif shape.shape_type == 13:  # 13 = imagen
                try:
                    img = Image.open(io.BytesIO(shape.image.blob))
                    text = pytesseract.image_to_string(img)
                    full_text.append(text.strip())
                except Exception as e:
                    print(f"Error en OCR: {e}")
    
    return "\n\n".join(filter(None, full_text))