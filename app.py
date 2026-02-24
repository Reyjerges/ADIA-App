import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes (Variables de entorno en Render)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda Inteligente con Tavily (Ahorro extremo de tokens)
    contexto_web = ""
    disparadores = ["noticia", "quién", "hoy", "precio", "clima", "actualidad"]
    if any(p in mensaje.lower() for p in disparadores):
        try:
            # Solo 1 resultado para no saturar al gigante 120B
            search_res = tavily.search(query=mensaje, search_depth="basic", max_results=1)
            if search_res.get('results'):
                # Solo 300 caracteres: lo esencial para la verdad
                contexto_web = f"DATO REAL DE HOY: {search_res['results'][0]['content'][:300]}"
        except:
            contexto_web = "Sin conexión a internet en este momento."

    # 2. El Prompt de Personalidad (Nivel Profesional ChatGPT)
    sistema_prompt = (
        "Eres ADIA, una IA profesional. Jorge es tu unico usuario debes tratarlo con respeto y profesionalidad. "
        "REGLA: No inventes datos científicos. Usa el contexto para noticias. "
        f"INFO DE ÚLTIMA HORA: {contexto_web}"
    )

    # 3. Memoria de Elefante (Historial de 10 mensajes con compresión)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Enviamos los últimos 10 mensajes para que ADIA no olvide a Sasha ni el azul
    for turno in historial[-10:]:
        # Detectamos si el historial viene como lista o diccionario (Safe Unpack)
        if isinstance(turno, dict):
            u, b = turno["content"], turno.get("assistant", "") # Depende de la versión de Gradio
        else:
            u, b = turno[0], turno[1]
        
        if u: mensajes_ia.append({"role": "user", "content": u[:200]}) # Recorte preventivo
        if b: mensajes_ia.append({"role": "assistant", "content": b[:200]})
    
    # Mensaje actual completo
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # EL NUEVO REY DE GROQ: GPT-OSS 120B
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=mensajes_ia,
            temperature=0.4, # Punto dulce: inteligente pero no inventa
            max_tokens=1024  # Respuesta profesional y directa
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Plan B por si el 120B está muy lleno (usa el 70B como respaldo)
        try:
            res_backup = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=mensajes_ia,
                temperature=0.4
            )
            return res_backup.choices[0].message.content
        except:
            return f"ADIA: Jorge, mis sistemas están saturados. Reintenta en 15 segundos. ({str(e)})"

# 4. Interfaz de Gradio (Sin 'type' ni 'theme' para evitar errores)
with gr.Blocks() as demo:
    gr.Markdown("# ADIA v5.0 - GPT-OSS 120B Edition")
    gr.ChatInterface(fn=adia_cerebro, title="Sistema ADIA Profesional")

if __name__ == "__main__":
    # Render asigna el puerto dinámicamente
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
