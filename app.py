import os
import time
import requests
import gradio as gr

# Configuración de API
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
# El puerto se obtiene del entorno (común en despliegues como Hugging Face o Render) o usa el 7860
PORT = int(os.environ.get("PORT", 7860))

def chat_with_gemini(message, history):
    """
    Función de chat con Gemini API y manejo de reintentos.
    """
    if not API_KEY:
        return "Error: No se encontró la GEMINI_API_KEY. Configúrala en las variables de entorno."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": message}]
        }]
    }

    # Reintentos con backoff exponencial
    for i in range(5):
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                return "Respuesta vacía del modelo."
            
            elif response.status_code == 429:
                time.sleep(2 ** i)
                continue
            else:
                return f"Error {response.status_code}: {response.text}"
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    return "Máximo de reintentos alcanzado."

# Solución al TypeError: Eliminamos 'theme' del constructor y usamos gr.Blocks si es necesario, 
# o simplemente dejamos que Gradio use el tema por defecto para máxima compatibilidad.
demo = gr.ChatInterface(
    fn=chat_with_gemini,
    title="Asistente Gemini",
    description="Interfaz de chat profesional con puerto dinámico.",
    examples=["¿Cómo funciona una API?", "Dame una receta de café"],
)

if __name__ == "__main__":
    # Lanzamiento con el puerto configurado
    # server_name "0.0.0.0" es vital para contenedores y despliegues externos
    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT
    )
