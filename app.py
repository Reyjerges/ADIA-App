import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes (Variables de entorno en Render)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de Noticias con Tavily (Dieta estricta de tokens)
    contexto_web = ""
    disparadores = ["noticia", "quién", "hoy", "precio", "clima", "actualidad", "pasó"]
    if any(p in mensaje.lower() for p in disparadores):
        try:
            # Solo 1 resultado para ahorrar espacio en el modelo 120B
            search_res = tavily.search(query=mensaje, search_depth="basic", max_results=1)
            if search_res.get('results'):
                # 300 caracteres es suficiente para la verdad científica
                contexto_web = f"DATO REAL DE HOY: {search_res['results'][0]['content'][:300]}"
        except:
            contexto_web = "Información de internet no disponible."

    # 2. Sistema Prompt Profesional (Personalidad ADIA)
    sistema_prompt = (
        f"Eres ADIA, una IA profesional de Grado Especial. Jorge es tu prioridad absoluta. "
        f"REGLA DE ORO: No inventes datos. Usa el contexto para noticias. "
        f"Si no sabes algo, admítelo y ofrece fuentes confiables. "
        f"CONTEXTO WEB ACTUAL: {contexto_web}"
    )

    # 3. MEMORIA EXPANDIDA (Últimos 40 mensajes / 20 turnos completos)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Procesamos el historial para que Groq lo entienda perfecto
    for turno in historial[-40:]:
        # Gradio puede enviar el historial como lista de listas [user, bot]
        if isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})
        # O como diccionario según la versión de Gradio
        elif isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role", "user"), "content": turno.get("content", "")})
    
    # Añadimos el mensaje actual de Jorge
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # EL NUEVO REY DE GROQ: GPT-OSS 120B
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=mensajes_ia,
            temperature=0.4,
            max_tokens=2000 # Permitimos respuestas largas para que no se corte
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Plan de Respaldo: Si el 120B falla, intenta con el 70B
        try:
            res_backup = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=mensajes_ia,
                temperature=0.4,
                max_tokens=1000
            )
            return res_backup.choices[0].message.content
        except:
            return f"ADIA: Jorge, mis sistemas están en alta demanda (Rate Limit). Reintenta en 30 segundos. Error: {str(e)}"

# 4. Interfaz de Gradio (Limpia para evitar TypeErrors en Render)
with gr.Blocks() as demo:
    gr.Markdown("# ADIA v6.0 - GPT-OSS 120B & Tavily")
    gr.ChatInterface(
        fn=adia_cerebro,
        title="Asistente ADIA Profesional",
        description="Memoria expandida (40 mensajes) e inteligencia de 120B."
    )

if __name__ == "__main__":
    # Render requiere leer el puerto dinámico
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
