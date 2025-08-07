FROM python:3.10-slim

WORKDIR /app

# 1. Dependencias del sistema (optimizado)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    ghostscript \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalación de dependencias Python (en dos etapas para mejor caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install pymupdf==1.22.5 pdf2image==1.16.3 --force-reinstall

# 3. Copia de código con estructura correcta
COPY src/ src/
COPY assets/ assets/

# 4. Configuración de entorno (actualizada)
ENV PYTHONPATH=/app/src:/app
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# 5. Configuración de Gunicorn (mejorada para IA)
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "--workers", "1", "src.main:app"]