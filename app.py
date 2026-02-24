import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda con Tavily (Solo si es necesario)
    contexto_web = ""
    disparadores = ["noticia", "quién", "qué pasó", "hoy", "precio", "clima", "mencho"]
    if any(p in mensaje.lower() for p in disparadores):
        try:
            search_result = tavily.search(query=mensaje, search_depth="basic", max_results=2)
            for r in search_result.get('results', []):
                contexto_web += f"DATO: {r['content'][:500]}\n"
        except:
            pass

    # 2. Instrucciones Profesionales
       # 2. Instrucciones Profesionales (AJUSTADAS)
        # 2. Instrucciones de ADIA (Versión Blindada v4.1)
    sistema_prompt = (
        "Eres ADIA, una IA profesional. Tu prioridad absoluta es Jorge. "
        "REGLA DE ORO: Tienes acceso a internet real mediante Tavily. No digas que tu base es de 2023. "
        "VERACIDAD: Si no estás 100% segura de un dato científico o técnico, NO LO INVENTES. "
        "En su lugar, explica lo que sí sabes con certeza y proporciona enlaces o fuentes de confianza "
        "(como Wikipedia, National Geographic o revistas científicas) donde Jorge pueda verificarlo. "
        f"CONTEXTO WEB ACTUAL: {contexto_web}"
    )


    # 3. RECONSTRUCCIÓN DE MEMORIA SIN ERRORES (Safe Unpack)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Procesamos el historial de forma segura para evitar ValueError
    for turno in historial:
        # Si Gradio manda Diccionarios (Versión nueva)
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno["role"], "content": turno["content"]})
        # Si Gradio manda Listas/Tuplas (Versión vieja)
        elif isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})
    
    # Añadimos la pregunta actual
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Usamos Llama 3.1 8B para evitar bloqueos por Rate Limit
        completion = groq_client.chat.completions.create(
              model="qwen-2.5-coder-32b",
            messages=mensajes_ia,
            temperature=0.4
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ADIA: Error de comunicación ({str(e)})"

# 4. Interfaz compatible con Render
with gr.Blocks() as demo:
    gr.Markdown("# ADIA v4.1 - Inteligencia Artificial")
    # No usamos 'type' ni 'theme' para evitar errores previos
    gr.ChatInterface(fn=adia_cerebro)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
