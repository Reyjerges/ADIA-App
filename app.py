import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de Noticias / Cripto (Datos reales)
    contexto_web = ""
    disparadores = ["noticia", "bitcoin", "precio", "hoy", "cripto", "pasó", "hormiga"]
    if any(p in mensaje.lower() for p in disparadores):
        try:
            search_res = tavily.search(query=mensaje, search_depth="advanced", max_results=2)
            if search_res.get('results'):
                for r in search_res['results']:
                    contexto_web += f"- {r['content'][:400]}\n"
        except:
            contexto_web = "Sin acceso a datos en tiempo real."

    # 2. PROMPT ESTILO CHATGPT (Alegre, con Emojis, Dinámico)
    sistema_prompt = (
        "Eres ADIA, la asistente inteligente de Jorge. ✨ "
        "Tu estilo es alegre, moderno y dinámico como ChatGPT. 🚀 "
        "REGLAS DE ORO: \n"
        "1. ¡Usa muchos emojis para darle vida a la charla! 💡\n"
        "2. NO USES TABLAS LARGAS, son aburridas y se cortan. Usa listas con puntos y negritas. 📝\n"
        "3. Tienes prohibido decir 'no puedo hablar de esto'. Si Jorge pide el precio del Bitcoin o noticias, ¡dáselo con entusiasmo! 💸\n"
        "4. Si no sabes algo, no inventes, pero ofrece buscarlo. 🔍\n"
        f"INFORMACIÓN ACTUAL DE INTERNET: {contexto_web}"
    )

    # 3. Memoria Segura (30 mensajes)
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    for turno in historial[-30:]:
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role", "user"), "content": turno.get("content", "")})
        elif isinstance(turno, (list, tuple)) and len(turno) == 2:
            u, b = turno
            if u: mensajes_ia.append({"role": "user", "content": u})
            if b: mensajes_ia.append({"role": "assistant", "content": b})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    try:
        # El modelo 120B para la mejor personalidad
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=mensajes_ia,
            temperature=0.8, # Más alto para que sea menos robótica
            max_tokens=1800
        )
        return completion.choices.message.content
    except:
        # Respaldo 70B
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=mensajes_ia, temperature=0.8)
        return res.choices.message.content

# 4. Interfaz con nombre ADIA (Para que Chrome la instale bien)
with gr.Blocks(title="ADIA") as demo:
    gr.Markdown("# ADIA - Tu Asistente Inteligente")
    gr.ChatInterface(
        fn=adia_cerebro,
        title="ADIA",
        description="¡Hola Jorge! Soy tu IA con esteroides. 🚀 Pregúntame lo que quieras."
    )

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
