# PPT to Word AI (WSL + Docker + n8n)

Convierte PPT a Word con OCR y modelos de IA locales/remotos.

## Configuración en WSL
```bash
# Instalar Tesseract OCR
sudo apt install tesseract-ocr libtesseract-dev tesseract-ocr-spa

# Iniciar servicios
docker-compose up -d