import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de Noticias con Tavily (Filtro de Realidad)
    contexto_web = ""
    disparadores = ["noticia", "hoy", "pasó", "quién", "precio", "clima"]
    
    if any(p in mensaje.lower() for p in disparadores):
        try:
            # Forzamos búsqueda con la fecha de hoy 23 de febrero 2026
            busqueda = tavily.search(query="noticias reales hoy 23 febrero 2026", search_depth="advanced", max_results=2)
            if busqueda.get('results'):
                for r in busqueda['results']:
                    contexto_web += f"HECHO REAL: {r['content'][:400]}\n"
        except:
            contexto_web = "SISTEMA: Error de conexión a Internet. No hay datos reales."

    # 2. Sistema Prompt (Anti-Alucinaciones)
    sistema_prompt = (
        "Eres ADIA, asistente profesional de Jorge. Jorge es tu prioridad. "
        "REGLA DE ORO: Si no hay datos en el 'CONTEXTO', no inventes noticias ni deportes. "
        "Diga la verdad. No hables de equipos inventados (Titans/Sharks). "
        f"CONTEXTO REAL HOY: {contexto_web}"
    )

    # 3. CONSTRUCCIÓN DE MEMORIA SEGURA (Evita el ValueError)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    # Recorremos el historial con los últimos 30 mensajes
    for turno in historial[-30:]:
        # CASO 1: Es un diccionario (Versión nueva de Gradio)
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        # CASO 2: Es una lista de 2 elementos [user, bot] (Versión vieja)
        elif isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})
    
    # Añadimos la pregunta actual de Jorge
    mensajes_ia.append({"role": "user", "content": mensaje})

    # 4. Bucle de Modelos (120B primero, luego 70B)
    for modelo in ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
        try:
            completion = groq_client.chat.completions.create(
                model=modelo, 
                messages=mensajes_ia,
                temperature=0.1, # Muy baja para evitar mentiras
                max_tokens=1200
            )
            return completion.choices[0].message.content
        except Exception:
            continue 

    return "ADIA: Jorge, mis motores están saturados. Reintenta en 15 segundos."

# 5. Interfaz de Gradio (Sin parámetros conflictivos para Render)
with gr.Blocks() as demo:
    gr.ChatInterface(fn=adia_cerebro, title="ADIA v6.7")

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
