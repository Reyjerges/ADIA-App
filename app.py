import os
from fastapi import FastAPI, Form, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from tavily import TavilyClient

app = FastAPI(title="ADIA Secure Engine")

# 1. SEGURIDAD: Configuración de CORS restringida
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, cámbialo por el dominio de tu app si es web
    allow_methods=["POST"], # Solo permitimos enviar mensajes
    allow_headers=["X-ADIA-KEY", "Content-Type"],
)

# 2. CLIENTES: Motores de IA y Búsqueda
# Asegúrate de poner estas 3 llaves en las Environment Variables de Render
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
ADIA_APP_SECRET = os.environ.get("ADIA_APP_SECRET") # Crea una contraseña larga aquí

# 3. SEGURIDAD: Función para verificar que la petición viene de TU App
def verificar_llave(x_adia_key: str = Header(None)):
    if x_adia_key != ADIA_APP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permiso para hablar con ADIA"
        )

@app.post("/chat")
async def chat_adia(mensaje: str = Form(...), x_adia_key: str = Header(None)):
    # Validamos la seguridad antes de procesar nada
    verificar_llave(x_adia_key)

    msg_low = mensaje.lower()
    necesita_internet = any(word in msg_low for word in ["busca", "precio", "noticias", "hoy", "quien es"])

    contexto_web = ""
    if necesita_internet:
        # Búsqueda en tiempo real con Tavily
        search_results = tavily_client.search(query=mensaje, search_depth="advanced")
        contexto_web = "\n\nINFORMACIÓN REAL DE INTERNET:\n" + str(search_results)

    # Prompt maestro
    sys_prompt = (
        "Eres ADIA, la IA de JORGE. Eres técnica, brillante y usas **negritas**. "
        "Si recibes contexto de internet, úsalo para dar una respuesta actualizada."
        "no uses tablas son feas y gastan tokens en su lugar usa listas con puntos."
        "usa emojis pero no exageres poniendo demasiados usalos para darle vida a la conversacion."
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"{mensaje} {contexto_web}"}
            ],
            temperature=0.6
        )
        return {"respuesta": completion.choices[0].message.content}
    except Exception as e:
        return {"respuesta": "⚠️ **Error en la matriz**: No pude procesar tu solicitud."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
