def adia_normal_chat(message, history):
    try:
        if not api_key:
            return "❌ Falta la API Key en Render."
            
        messages = [{"role": "system", "content": "Eres ADIA, una IA avanzada."}]
        
        for turn in history:
            if isinstance(turn, dict):
                # LIMPIEZA CLAVE: Solo enviamos 'role' y 'content', eliminamos 'metadata'
                clean_turn = {
                    "role": turn.get("role"),
                    "content": turn.get("content")
                }
                # Solo añadir si ambos campos existen
                if clean_turn["role"] and clean_turn["content"]:
                    messages.append(clean_turn)
            elif isinstance(turn, (list, tuple)) and len(turn) == 2:
                messages.append({"role": "user", "content": turn[0]})
                messages.append({"role": "assistant", "content": turn[1]})
            
        messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=messages
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error: {str(e)}"
