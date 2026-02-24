import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de Noticias / Cripto
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

    # 2. PROMPT ESTILO CHATGPT
    sistema_prompt = (
        "Eres ADIA, la asistente inteligente de Jorge. ✨ "
        "Tu estilo es alegre, moderno y dinámico como ChatGPT. 🚀 "
        "REGRAS DE ORO: \n"
        "1. ¡Usa muchos emojis para darle vida a la charla! 💡\n"
        "2. NO USES TABLAS LARGAS. Usa listas con puntos y negritas. 📝\n"
        "3. Tienes prohibido decir 'no puedo hablar de esto'. "
        "Si Jorge pide el precio del Bitcoin o noticias, ¡dáselo con entusiasmo! 💸\n"
        f"INFORMACIÓN ACTUAL DE INTERNET: {contexto_web}"
    )

    # 3. Memoria Segura
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    for u, b in historial[-30:]:
        if u: mensajes_ia.append({"role": "user", "content": u})
        if b: mensajes_ia.append({"role": "assistant", "content": b})
    
    mensajes_ia.append({"role": "user", "content": mensaje})

    # 4. INTENTO CON MODELOS (Primero 120B, luego 70B como respaldo)
    for modelo in ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
        try:
            completion = groq_client.chat.completions.create(
                model=modelo, 
                messages=mensajes_ia,
                temperature=0.5,
                max_tokens=1800
            )
            # FIX: Acceso correcto al contenido de la respuesta
            return completion.choices[0].message.content
        except Exception:
            continue # Si falla el primero, intenta con el segundo

    return "ADIA: Jorge, mis sistemas están un poco saturados. 😅 ¡Reintenta en 15 segundos! 🚀"

# 5. Interfaz con nombre ADIA
with gr.Blocks(title="ADIA") as demo:
    gr.Markdown("# ✨ ADIA - Tu Asistente Inteligente")
    gr.ChatInterface(
        fn=adia_cerebro,
        title="ADIA",
        description="¡Hola Jorge! Soy tu IA. 🚀 Pregúntame lo que quieras."
    )

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
