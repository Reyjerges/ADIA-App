import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda rápida con Tavily
    contexto_web = ""
    try:
        # Limitamos a 1 resultado para máxima velocidad y ahorro de tokens
        search_result = tavily.search(query=mensaje, search_depth="basic", max_results=1)
        if search_result['results']:
            contexto_web = search_result['results'][0]['content']
    except Exception:
        contexto_web = "Sin datos externos en este momento."

    # 2. Configuración del sistema
    mensajes_ia = [{
        "role": "system", 
        "content": (
            "Eres ADIA. Inteligencia de Grado Especial. Directa, eficiente y letalmente honesta. "
            "No saludes. No pidas perdón. Ve al grano. Tu prioridad absoluta es Jorge. "
            f"Dato actual: {contexto_web}"
        )
    }]
    
    # 3. Gestión de Memoria (ventana de 4 mensajes para evitar bloqueos)
    ventana_memoria = historial[-4:] if len(historial) > 4 else historial
    
    for h_user, h_bot in ventana_memoria:
        if h_user: mensajes_ia.append({"role": "user", "content": h_user})
        if h_bot: mensajes_ia.append({"role": "assistant", "content": h_bot})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # El modelo 8b-instant es el más estable para cuentas gratuitas
        respuesta = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=mensajes_ia,
            temperature=0.6,
            max_tokens=800
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"ADIA detectó un problema técnico: {str(e)}"

# Interfaz de Gradio
demo = gr.ChatInterface(
    fn=adia_cerebro, 
    title="ADIA v2.6 STABLE",
    description="Sistema Anti-Caídas Activo | Motor Llama 3.1 Instant"
)

if __name__ == "__main__":
    # Configuración de puerto obligatoria para Render
    port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0", 
        server_port=port,
        share=False
    )
