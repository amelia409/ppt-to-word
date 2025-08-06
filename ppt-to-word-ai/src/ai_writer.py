from ollama import Client
import os

def generate_explanation(content: str) -> str:
    """Genera explicación mejorada con formato"""
    client = Client(host=f"http://{os.getenv('OLLAMA_HOST', 'ollama')}:11434")
    
    prompt = """Transforma este contenido en material didáctico profesional con:
    1. Título resaltado (##)
    2. Puntos clave con viñetas
    3. Explicaciones claras
    4. Notas técnicas entre comillas
    5. Lenguaje formal pero accesible
    
    Contenido original:
    {content}"""
    
    response = client.generate(
        model="llama3",
        prompt=prompt.format(content=content),
        options={
            "temperature": 0.7,
            "num_ctx": 4096
        }
    )
    return response["response"]