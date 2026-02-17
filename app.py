def responder_adia(mensaje, historial):
    if not api_key:
        return "Error: Configura la GROQ_API_KEY."

    system_prompt = (
        "Eres ADIA, el sistema operativo de Jorge. "
        "Eres experta en robótica y hardware. Responde de forma técnica y breve."
    )
    
    mensajes_api = [{"role": "system", "content": system_prompt}]
    
    # LIMPIEZA DEL HISTORIAL: Extraemos solo el texto para evitar el error 400
    for interaccion in historial:
        # En versiones nuevas, 'interaccion' puede ser un diccionario con metadatos
        if isinstance(interaccion, dict):
            role = interaccion.get("role")
            content = interaccion.get("content")
            if role and content:
                mensajes_api.append({"role": role, "content": str(content)})
        elif isinstance(interaccion, (list, tuple)):
            # Formato antiguo: [user, assistant]
            u, b = interaccion
            if u: mensajes_api.append({"role": "user", "content": str(u)})
            if b: mensajes_api.append({"role": "assistant", "content": str(b)})

    # Añadir mensaje actual
    mensajes_api.append({"role": "user", "content": str(mensaje)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_api,
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"
