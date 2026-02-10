import os
import time
import requests
import gradio as gr

# Configuración de API y Red
# El entorno proporciona la clave automáticamente si está configurada como GEMINI_API_KEY
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
# Configuración del puerto para el despliegue
PORT = int(os.environ.get("PORT", 7860))

def chat_with_gemini(message, history):
    """
    Función de chat con manejo de errores y reintentos (Exponential Backoff).
    """
    if not API_KEY:
        return "Error: No se encontró la GEMINI_API_KEY en las variables de entorno."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    # Estructura de la solicitud para Gemini
    payload = {
        "contents": [{
            "parts": [{"text": message}]
        }]
    }

    # Implementación de reintentos para evitar errores de cuota (429) con backoff exponencial
    for i in range(5):
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Extraer el texto de la respuesta del JSON de Gemini
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                return "El modelo devolvió una respuesta vacía."
            
            elif response.status_code == 429:
                # Si hay demasiadas solicitudes, esperar (1s, 2s, 4s, 8s, 16s) y reintentar
                time.sleep(2 ** i)
                continue
            
            else:
                return f"Error del servidor (Código {response.status_code}): {response.text}"
        
        except requests.exceptions.RequestException as e:
            return f"Error de conexión: {str(e)}"
    
    return "Se agotaron los reintentos debido a la alta carga del servicio."

# Creación de la interfaz de Gradio
demo = gr.ChatInterface(
    fn=chat_with_gemini,
    title="Asistente Gemini con Puerto Configurado",
    description="Chatbot listo para despliegue con configuración dinámica de puerto.",
    theme="soft",
    examples=["¿Cuál es la diferencia entre HTTP y HTTPS?", "Escribe una función en Python para ordenar una lista"],
    cache_examples=False
)

if __name__ == "__main__":
    # Lanzar la aplicación especificando el puerto y host
    # server_name="0.0.0.0" permite que la app sea accesible externamente
    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT
    )
