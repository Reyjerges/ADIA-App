import os
import re
import sys

# Manejo de dependencias para Render
try:
    import gradio as gr
    from groq import Groq
except ImportError as e:
    print(f"ERROR: Falta una librería: {e}")
    sys.exit(1)

# --- CONFIGURACIÓN ---
port = int(os.environ.get("PORT", 10000))
api_key = os.environ.get("GROQ_API_KEY")
client = None

if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"Error al inicializar Groq: {e}")

def buscar_en_google(consulta):
    """Búsqueda opcional para dar contexto actual a ADIA."""
    try:
        from googlesearch import search
        resultados = list(search(consulta, num_results=3, lang="es"))
        if resultados:
            return "\n\n--- INFO WEB RECIENTE ---\n" + "\n".join(resultados)
        return ""
    except:
        return ""

def chat_adia(mensaje, historial):
    if not client:
        return "ADIA: Hola. Por favor, configura la clave 'GROQ_API_KEY' en Render para activarme."

    # Instrucciones específicas para que ADIA use CANVAS correctamente
    instrucciones = (
        "Eres ADIA, una IA experta en desarrollo de videojuegos con HTML5 Canvas. "
        "Cuando el usuario pida un juego o algo visual, responde con UN SOLO bloque de código ```html ... ```. "
        "Reglas del código: "
        "1. Usa <canvas id='gameCanvas'></canvas> y CSS para que ocupe el 100% de la ventana. "
        "2. Todo el JavaScript debe ir dentro de etiquetas <script>. "
        "3. El juego debe ser autocontenido (sin archivos externos). "
        "4. Usa figuras geométricas (rect, arc) para los gráficos. "
        "5. Asegúrate de que los controles sean por teclado o clic."
    )

    contexto_web = ""
    if any(p in mensaje.lower() for p in ["busca", "internet", "noticias", "quien es"]):
        contexto_web = buscar_en_google(mensaje)

    mensajes_api = [{"role": "system", "content": instrucciones}]
    
    for usuario, asistente in
