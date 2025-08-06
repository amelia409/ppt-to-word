import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(file_path: str) -> list:
    """Extrae texto estructurado de PDF"""
    doc = fitz.open(file_path)
    pages_data = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_data = {
            "page_number": page_num+1,
            "content": [],
            "images": []
        }
        
        # Extraer texto
        text = page.get_text("text")
        if text.strip():
            page_data["content"].append({
                "type": "text",
                "data": text
            })
        
        # Procesar imágenes
        for img in page.get_images():
            try:
                base_image = doc.extract_image(img[0])
                image_bytes = base_image["image"]
                
                # OCR
                text = pytesseract.image_to_string(Image.open(io.BytesIO(image_bytes)))
                page_data["images"].append({
                    "image": image_bytes,
                    "text": text.strip()
                })
            except Exception as e:
                print(f"Error procesando imagen PDF: {e}")
        
        pages_data.append(page_data)
    
    return pages_data