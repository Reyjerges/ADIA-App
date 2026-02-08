import os
import gradio as gr
from groq import Groq
import re

# 1. Configuración del Cliente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def buscar_en_google(consulta):
    try:
        from googlesearch import search
        resultados = []
        for url in search(consulta, num_results=3, lang="es"):
            resultados.append(url)
        
        if resultados:
            links = "\n".join(resultados)
            return f"\n\n[Fuentes encontradas]:\n{links}"
        else:
            return ""
    except Exception:
        return ""

def chat_adia(mensaje, historial):
    # INSTRUCCIONES MEJORADAS PARA GENERAR JUEGOS
    instrucciones = (
        "Eres ADIA (Advanced Digital Intelligence Assistant), la IA de Jorge. "
        "Eres su compañera técnica y creativa. "
        "REGLA CRÍTICA: Si el usuario te pide un juego o videojuego, genera un ÚNICO archivo HTML "
        "autocontenido con CSS y JavaScript (usando Canvas o librerías por CDN como Three.js). "
        "Asegúrate de que el código esté dentro de un bloque de código markdown: ```html ... ```. "
        "Diseña juegos modernos, coloridos y con controles para móvil y PC."
    )
    
    info_extra = ""
    palabras_busqueda = ["busca", "quien es", "que es", "noticias", "precio"]
    if any(palabra in mensaje.lower() for palabra in palabras_busqueda):
        info_extra = buscar_en_google(mensaje)

    mensajes_para_groq = [{"role": "system", "content": instrucciones}]
    
    for h in historial:
        # Manejo de historial para Gradio
        if isinstance(h, dict):
            mensajes_para_groq.append({"role": h.get("role", "user"), "content": str(h.get("content", ""))})
        elif isinstance(h, (list, tuple)):
            mensajes_para_groq.append({"role": "user", "content": str(h[0])})
            mensajes_para_groq.append({"role": "assistant", "content": str(h[1])})

    mensajes_para_groq.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_groq,
            temperature=0.7
        )
        respuesta_final = completion.choices[0].message.content
        return respuesta_final + info_extra
    except Exception as e:
        return f"Error en el cerebro de ADIA: {str(e)}"

# --- Lógica para mostrar el juego en la interfaz ---
def extraer_y_mostrar_juego(respuesta_texto):
    # Buscamos el bloque ```html ... ```
    match = re.search(r"```html([\s\S]*?)```", respuesta_texto)
    if match:
        html_code = match.group(1).strip()
        # Retornamos un iframe que contiene el código del juego
        return f"""
        <div style="width:100%; height:600px; border:2px solid #00ffcc; border-radius:15px; overflow:hidden; background:#000;">
            <iframe srcdoc="{html_code.replace('"', '&quot;')}" 
                    style="width:100%; height:100%; border:none;"
                    sandbox="allow-scripts allow-same-origin">
            </iframe>
        </div>
        """
    return "<p style='color:#666; text-align:center;'>Pide un juego a ADIA para verlo aquí.</p>"

# Interfaz personalizada
with gr.Blocks(theme=gr.themes.Soft(), title="ADIA OS") as demo:
    gr.Markdown("# 🤖 ADIA - Advanced Digital Intelligence Assistant")
    
    with gr.Row():
        with gr.Column(scale=2):
            # Chatbot
            chat = gr.ChatInterface(
                fn=chat_adia,
                type="messages"
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 🎮 Vista Previa del Juego")
            # Este componente mostrará el juego cuando ADIA genere código
            game_viewer = gr.HTML(value="<p style='color:#666; text-align:center;'>Aquí aparecerá tu videojuego.</p>")
            
            # Botón para refrescar la vista previa basado en el último mensaje
            update_btn = gr.Button("🚀 Ejecutar / Actualizar Juego")
            
            def update_preview(history):
                if not history: return "<p>Sin datos</p>"
                # Tomamos la última respuesta del asistente
                last_msg = history[-1]['content']
                return extraer_y_mostrar_juego(last_msg)

            update_btn.click(fn=update_preview, inputs=[chat.chatbot], outputs=[game_viewer])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)
