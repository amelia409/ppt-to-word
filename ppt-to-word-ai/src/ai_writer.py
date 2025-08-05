from ollama import Client
import os

def generate_explanation(text: str, model: str = "llama3") -> str:
    """
    Genera una explicación didáctica usando Ollama
    
    Args:
        text: Texto a explicar
        model: Modelo de IA a usar
    
    Returns:
        Explicación generada
    """
    try:
        client = Client(host=f"http://{os.getenv('OLLAMA_HOST', 'ollama')}:11434")
        response = client.generate(
            model=model,
            prompt=f"Explica este contenido para universitarios en español, sé conciso pero didáctico:\n\n{text}"
        )
        return response["response"]
    except Exception as e:
        print(f"Error en generación IA: {e}")
        return text  # Fallback al texto original