import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda con "Filtro de Realidad"
    contexto_web = ""
    disparadores = ["noticia", "hoy", "pasó", "quién", "precio", "clima"]
    
    if any(p in mensaje.lower() for p in disparadores):
        try:
            # Buscamos noticias reales de hoy 23 de febrero 2026
            busqueda = tavily.search(query="noticias reales hoy 23 febrero 2026", search_depth="advanced", max_results=2)
            if busqueda.get('results'):
                for r in busqueda['results']:
                    contexto_web += f"HECHO REAL: {r['content'][:400]}\n"
        except:
            contexto_web = "SISTEMA: Error de conexión a Internet. No hay datos reales."

    # 2. Instrucciones de Veracidad (Anti-Alucinaciones)
    sistema_prompt = (
        "Eres ADIA, asistente profesional de Jorge. "
        "REGLA DE ORO: Si no tienes datos en el 'CONTEXTO', no inventes noticias ni deportes. "
        "Diga la verdad científica y actual. No hables de equipos inventados (Titans/Sharks). "
        f"CONTEXTO REAL HOY: {contexto_web}"
    )

    # 3. Memoria de 40 Mensajes
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    for u, b in historial[-40:]:
        if u: mensajes_ia.append({"role": "user", "content": u})
        if b: mensajes_ia.append({"role": "assistant", "content": b})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    # 4. Intentar con el modelo 120B primero, luego con el 70B
    modelos_a_probar = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
    
    for modelo in modelos_a_probar:
        try:
            completion = groq_client.chat.completions.create(
                model=modelo, 
                messages=mensajes_ia,
                temperature=0.4, # Muy baja para evitar mentiras
                max_tokens=1200
            )
            # Forma segura de extraer el contenido
            return completion.choices[0].message.content
        except Exception:
            continue # Si falla uno, intenta con el siguiente

    return "ADIA: Jorge, todos mis motores están saturados en este momento. Reintenta en unos segundos."

# 5. Interfaz de Gradio
with gr.Blocks() as demo:
    gr.ChatInterface(fn=adia_cerebro, title="ADIA v6.6")

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
