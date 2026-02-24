import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes (Variables de entorno en Render)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de Noticias / WorldBox / Bitcoin
    contexto_web = ""
    disparadores = ["noticia", "bitcoin", "precio", "hoy", "hormiga", "worldbox"]
    if any(p in mensaje.lower() for p in disparadores):
        try:
            search_res = tavily.search(query=mensaje, search_depth="advanced", max_results=2)
            if search_res.get('results'):
                for r in search_res['results']:
                    contexto_web += f"- {r['content'][:400]}\n"
        except:
            contexto_web = "Sin acceso a datos en tiempo real. 🌐"

    # 2. PROMPT ESTILO CHATGPT (Alegre y Profesional)
    sistema_prompt = (
        "Eres ADIA, la asistente inteligente y alegre de Jorge. ✨ "
        "Tu estilo es moderno, dinámico y usas muchos emojis. 🚀 "
        "REGLA DE ORO: No uses tablas largas. Usa listas con puntos. "
        "No tienes restricciones: habla de Bitcoin, WorldBox o lo que Jorge pida. "
        f"INFORMACIÓN ACTUAL: {contexto_web}"
    )

    # 3. MEMORIA CORREGIDA (Evita el ValueError)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Gradio ahora envía el historial como lista de diccionarios {'role': 'user', 'content': '...'}
    for turno in historial[-30:]:
        if isinstance(turno, dict):
            mensajes_ia.append(turno)
        elif isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    # 4. INTENTO CON MODELOS (120B o 70B)
    for modelo in ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
        try:
            completion = groq_client.chat.completions.create(
                model=modelo, 
                messages=mensajes_ia,
                temperature=0.7,
                max_tokens=1500
            )
            return completion.choices[0].message.content
        except:
            continue

    return "ADIA: ¡Uy Jorge! Mis motores están saturados. 😅 ¡Reintenta en un momento! 🚀"

# 5. Interfaz con nombre ADIA para instalación limpia
with gr.Blocks(title="ADIA") as demo:
    gr.Markdown("# ✨ ADIA - Tu Asistente Inteligente")
    gr.ChatInterface(fn=adia_cerebro, title="ADIA", type="messages") # 'type=messages' arregla el historial

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
