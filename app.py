import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Configuración de Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda con "Candado de Verdad"
    contexto_web = ""
    disparadores = ["noticia", "hoy", "pasó", "quién", "precio", "hola", "clima"]
    
    if any(p in mensaje.lower() for p in disparadores):
        try:
            # Buscamos con fecha exacta para forzar a Tavily
            busqueda = tavily.search(query=f"noticias reales hoy 23 febrero 2026", search_depth="advanced", max_results=2)
            if busqueda.get('results'):
                for r in busqueda['results']:
                    contexto_web += f"HECHO REAL: {r['content'][:400]}\n"
        except:
            contexto_web = "SISTEMA: Error de conexión a Internet. No hay datos reales disponibles."

    # 2. Sistema Prompt "Anti-Fantasía"
    # Le prohibimos hablar de los Titans o Sharks y le exigimos honestidad
    sistema_prompt = (
        "Eres ADIA, asistente profesional de Jorge. "
        "REGLA SUPREMA: No inventes noticias, equipos de deportes o eventos futuros. "
        "Si el 'CONTEXTO' está vacío o dice ERROR, responde: 'Jorge, no tengo acceso a internet real ahora, no puedo darte noticias'. "
        "No alucines con los Miami Sharks o Los Angeles Titans, eso es falso. "
        f"CONTEXTO REAL (USA SOLO ESTO): {contexto_web}"
    )

    # 3. Memoria de 40 Mensajes con Safe Unpack
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    for turno in historial[-40:]:
        if isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})
        elif isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role", "user"), "content": turno.get("content", "")})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # Usamos el modelo 120B pero con temperatura mínima para evitar mentiras
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=mensajes_ia,
            temperature=0.4, # <--- CLAVE: Cero creatividad, solo hechos
            max_tokens=1500
        )
        return completion.choices.message.content
    except Exception as e:
        # Respaldo al 70B si el 120B falla
        try:
            res_backup = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=mensajes_ia,
                temperature=0.1
            )
            return res_backup.choices.message.content
        except:
            return f"ADIA: Jorge, mis sistemas están saturados. Inténtalo en 20 segundos. ({str(e)})"

# 4. Interfaz de Gradio
with gr.Blocks() as demo:
    gr.Markdown("# ADIA v6.5 - Anti-Alucinaciones Edition")
    gr.ChatInterface(fn=adia_cerebro, title="Sistema ADIA Profesional")

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
