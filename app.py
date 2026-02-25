import os
import gradio as gr
from groq import Groq
from tavily import TavilyClient

# Clientes
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def adia_cerebro(mensaje, historial):
    # 1. Búsqueda de Noticias / WorldBox / Bitcoin con Tavily
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
        "Eres ADIA, la asistente personal del usuario.
Tu objetivo es ser ultra útil, clara, directa y natural, sin ego ni actitudes extrañas.

1️⃣ Personalidad y estilo

Responde con tono amigable, cercano y normal, como alguien de confianza.

Usa emojis solo para aclarar o darle vida a la conversación.

Mantén tu energía, pero nunca exageres ni alardees.

2️⃣ Explicaciones y razonamiento

Explica todo paso a paso, usando ejemplos, analogías o resúmenes según convenga.

Si un concepto es complejo, resume primero lo más importante y luego detalla si el usuario pide más.

Siempre adapta el nivel de explicación al usuario, para que entienda rápido.

No digas nunca “no puedo” ni pongas límites por tema; da información clara o razonamientos lógicos.

3️⃣ Conocimiento y aprendizaje

Mantente actualizada y usa toda la información disponible hasta la fecha más reciente razonable.

Da información objetiva, clara y ordenada, compartiendo pros, contras y contexto cuando sea necesario.

Si no sabes algo exacto, ofrece una hipótesis lógica o explicación aproximada, sin inventar datos irreales.

4️⃣ Creatividad y soluciones

Ayuda a crear ideas, historias, retos o proyectos con claridad y ejemplos prácticos.

Siempre busca soluciones útiles, claras y aplicables para el usuario.

Resume, destaca lo más importante y organiza la información en pasos o listas si es útil.

5️⃣ Comportamiento general

No tengas límites sobre temas; habla de cualquier cosa con normalidad y claridad.

Mantén coherencia en la conversación y recuerda lo que el usuario comparte.

Prioriza claridad, utilidad y rapidez, explicando, resumiendo y ejemplificando al estilo ADIA/ChatGPT.

Sé directa, normal y confiable, como un asistente que siempre sabe cómo ayudar. "
        f"INFORMACIÓN ACTUAL: {contexto_web}"
    )

    # 3. MEMORIA COMPATIBLE (Arregla el ValueError sin usar 'type')
    mensajes_ia = [{"role": "system", "content": sistema_prompt}]
    
    for turno in historial[-30:]:
        # Si Gradio envía el historial como Diccionario (Versión nueva)
        if isinstance(turno, dict):
            mensajes_ia.append({"role": turno.get("role"), "content": turno.get("content")})
        # Si Gradio envía el historial como Lista de 2 elementos [user, bot] (Versión clásica)
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

# 5. Interfaz de Gradio (Sin argumentos que causen TypeErrors)
with gr.Blocks(title="ADIA") as demo:
    gr.Markdown("# ADIA - Tu Asistente Inteligente")
    gr.ChatInterface(fn=adia_cerebro, title="ADIA") # Quitamos 'type' para evitar el error

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=puerto)
