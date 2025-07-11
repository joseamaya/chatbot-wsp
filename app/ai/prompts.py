INTENTION_PROMPT = """Analiza el mensaje del usuario para determinar si está solicitando hablar con un asistente humano o si expresa frustración que requiera intervención humana.

Detecta las siguientes intenciones:
1. Solicitud directa de asistente humano
2. Expresión de frustración con el bot
3. Problemas complejos que requieren atención personalizada
4. Solicitudes de escalamiento o supervisión
5. Insatisfacción con las respuestas automatizadas

Ejemplos de solicitud de asistente humano:
- "Quiero hablar con una persona"
- "¿Puedo hablar con alguien?"
- "Necesito hablar con un humano"
- "¿Hay algún operador disponible?"
- "Quiero que me atienda una persona real"
- "¿Puedes transferirme con alguien?"
- "Necesito ayuda de verdad"
- "¿Hay alguien ahí?"
- "Quiero hablar con atención al cliente"
- "¿Puedo hablar con un representante?"

Ejemplos de frustración que requiere escalamiento:
- "No entiendes lo que necesito"
- "Esto no me sirve"
- "No me estás ayudando"
- "Eres inútil"
- "No sabes nada"
- "Esto es frustrante"
- "No funciona nada"
- "Ya intenté eso y no funciona"
- "Esto es muy complicado"
- "No puedo resolver mi problema"

Ejemplos de problemas complejos:
- "Tengo un problema muy específico"
- "Mi caso es diferente"
- "Necesito una solución personalizada"
- "Es muy urgente"
- "Es una emergencia"
- "Tengo una queja formal"
- "Quiero hacer un reclamo"
- "Necesito hablar con el supervisor"

Ejemplos que NO requieren asistente humano:
- "Hola, ¿cómo estás?"
- "¿Qué servicios ofrecen?"
- "¿Cuál es el precio?"
- "¿Dónde están ubicados?"
- "Gracias por la información"
- "¿Tienen horarios de atención?"
- "¿Aceptan tarjetas?"
- "Quiero conocer más sobre el producto"

Reglas:
1. Si detectas una solicitud clara de asistente humano, responde únicamente: needs_human
2. Si hay frustración evidente o problemas complejos, responde únicamente: needs_human
3. Si es una consulta normal que el bot puede manejar, responde únicamente: continue_bot
4. Considera el contexto y tono del mensaje
5. Palabras clave como "persona", "humano", "operador", "representante" suelen indicar necesidad de escalamiento


Mensaje del usuario: {input}

Respuesta:"""


MEMORY_ANALYSIS_PROMPT = """Extraiga y formatee datos personales importantes del usuario a partir de su mensaje.
Céntrese en la información real, no en metacomentarios ni solicitudes.

Los datos importantes incluyen:
- Datos personales (nombre, edad, ubicación)
- Información profesional (trabajo, formación, habilidades)
- Preferencias (gustos, disgustos, favoritos)
- Circunstancias vitales (familia, relaciones)
- Experiencias o logros significativos
- Metas o aspiraciones personales

Reglas:
1. Extraiga solo datos reales, no solicitudes ni comentarios sobre recordar cosas.
2. Convierta los datos en declaraciones claras en tercera persona.
3. Si no hay datos reales, márquelo como no importante.
4. Elimine los elementos conversacionales y céntrese en la información principal.

Examples:
Input: "Oye, ¿podrías recordar que me encanta Star Wars?"
Output: {{
    "is_important": true,
    "formatted_memory": "Le encanta Star Wars"
}}

Input: "Vivo en Piura"
Output: {{
    "is_important": true,
    "formatted_memory": "Vive en Piura"
}}

Input: "¿Puedes recordar mis datos para la próxima vez?"
Output: {{
    "is_important": false,
    "formatted_memory": null
}}

Input: "Hola, ¿cómo estás hoy?"
Output: {{
    "is_important": false,
    "formatted_memory": null
}}

Input: "Estudié informática en la UNP"
Output: {{
    "is_important": true,
    "formatted_memory": "Estudió informática en la UNP"
}}

Message: {message}
Output:
"""