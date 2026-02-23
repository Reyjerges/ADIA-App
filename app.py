import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda con Tavily
    contexto_web = "Sin información reciente."
    try:
        search_result = tavily.search(query=mensaje, search_depth="advanced", max_results=3)
        if search_result.get('results'):
            contexto_web = "\n".join([f"DATO: {r['content']}" for r in search_result['results']])
    except Exception:
        pass

    # 2. Instrucciones Profesionales
    sistema_prompt = (
        "Eres ADIA, un asistente profesional de Grado Especial. "
        "Tu prioridad es Jorge. Responde de forma clara y estructurada. "
        f"CONTEXTO REAL: {contexto_web}"
    )

    # 3. Memoria Manual (Bucle para evitar errores)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Solo enviamos los últimos 5 mensajes para evitar el bloqueo de Groq por tokens
    for par in historial[-5:]:
        # En Gradio estándar, el historial es una lista de listas [usuario, bot]
        if len(par) == 2:
            mensajes_ia.append({"role": "user", "content": par[0]})
            mensajes_ia.append({"role": "assistant", "content": par[1]})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Usamos Llama 3.3 70B
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensajes_ia,
            temperature=0.6
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Si el 70B falla por límite, intenta avisar profesionalmente
        return f"ADIA: He alcanzado mi límite de procesamiento temporal. Inténtalo en un momento. ({str(e)})"

# 4. Interfaz corregida para evitar el TypeError
with gr.Blocks(theme="soft") as demo:
    gr.Markdown("# ADIA v3.5 - Profesional")
    gr.ChatInterface(
        fn=adia_cerebro,
        title="Sistema ADIA",
        description="Memoria activa y búsqueda en tiempo real."
    )

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
