from pptx import Presentation
import pytesseract
from PIL import Image
import io
import re

def extract_structured_content(file_path: str) -> list:
    """Extrae contenido estructurado de PPTX"""
    prs = Presentation(file_path)
    slides_data = []
    
    for i, slide in enumerate(prs.slides):
        slide_data = {
            "slide_number": i+1,
            "title": "",
            "content": [],
            "images": []
        }
        
        for shape in slide.shapes:
            try:
                # Procesar texto
                if hasattr(shape, "text") and shape.text.strip():
                    text = clean_text(shape.text)
                    if is_title(shape, slide):
                        slide_data["title"] = text
                    else:
                        slide_data["content"].append({
                            "type": "text",
                            "data": text
                        })
                
                # Procesar imágenes
                elif hasattr(shape, "shape_type") and shape.shape_type == 13:
                    try:
                        img = Image.open(io.BytesIO(shape.image.blob))
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        slide_data["images"].append({
                            "image": img_byte_arr.getvalue(),
                            "description": get_shape_description(shape)
                        })
                    except Exception as e:
                        print(f"Error procesando imagen: {e}")
                        
            except Exception as e:
                print(f"Error procesando shape: {e}")
                continue
        
        slides_data.append(slide_data)
    return slides_data

def clean_text(text: str) -> str:
    """Limpia texto fragmentado"""
    return re.sub(r'(\w)\s*\n\s*(\w)', r'\1 \2', text)

def is_title(shape, slide) -> bool:
    """Determina si un shape es título de manera más robusta"""
    try:
        # Primera slide suele ser título
        if slide.slide_index == 0:
            return True
            
        # Verificar por nombre o contenido
        if hasattr(shape, 'name') and 'title' in shape.name.lower():
            return True
            
        # Verificar si es placeholder (método compatible con más versiones)
        if hasattr(shape, 'is_placeholder') and shape.is_placeholder:
            return True
            
        return False
    except:
        return False

def get_shape_description(shape) -> str:
    """Obtiene texto alternativo de shapes"""
    try:
        return shape.name if hasattr(shape, 'name') and shape.name else "Imagen"
    except:
        return "Imagen"