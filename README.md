# WhatsApp Chatbot (chatbot-wsp)

This project is a WhatsApp chatbot built with Python and FastAPI. It leverages natural language processing and vector storage to provide intelligent responses to WhatsApp messages.

## Project Structure

- `main.py`: Main entry point of the FastAPI application.
- `ai/`: AI logic, chains, nodes, embeddings, prompts, and vector storage.
- `config/settings.py`: General project configuration.
- `database/`: Database connection and dependencies.
- `routes/whatsapp.py`: FastAPI routes for WhatsApp integration.
- `requirements.txt`: Main dependencies.
- `requirements-dev.txt`: Development dependencies.
- `langgraph.json`: LangGraph configuration file.

## Requirements

- Python 3.12+
- FastAPI
- MongoDB (for vector storage)
- Langchain
- LangGraph

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joseamaya/chatbot-wsp.git
   cd chatbot-wsp
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Create environment file:**
   - cp .env.example .env.
   - Fill in the required environment variables in `.env`.

## Usage

1. **Run the FastAPI application:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Integrate with WhatsApp:**
   - Follow the instructions in `routes/whatsapp.py` to connect the bot with the WhatsApp API.

3. **Visualize and test the graph with LangGraph:**
   - To visualize or test the graph, use:
     ```bash
     langgraph dev
     ```
   - This will allow you to see the graph in action and run tests interactively.

## Docker Setup

El proyecto incluye dos configuraciones de Docker Compose:
- `docker-compose.dev.yml`: Para desarrollo local (incluye MongoDB)
- `docker-compose.prod.yml`: Para producción (se conecta a MongoDB Atlas)

#### Desarrollo Local

1. **Construir y arrancar los contenedores:**
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

2. **Arrancar en modo detached (opcional):**
   ```bash
   docker compose -f docker-compose.dev.yml up -d
   ```

3. **Detener los contenedores:**
   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

4. **Ver logs:**
   ```bash
   # Ver logs de todos los contenedores
   docker compose -f docker-compose.dev.yml logs

   # Ver logs de servicios específicos
   docker compose -f docker-compose.dev.yml logs app
   docker compose -f docker-compose.dev.yml logs mongo
   ```

#### Producción

1. **Configurar variables de entorno:**
   - Copiar `.env.prod.example` a `.env.prod`
   - Actualizar las variables con las credenciales de MongoDB Atlas

2. **Construir y arrancar el contenedor:**
   ```bash
   docker compose -f docker-compose.prod.yml up --build
   ```

3. **Arrancar en modo detached (opcional):**
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

4. **Detener el contenedor:**
   ```bash
   docker compose -f docker-compose.prod.yml down
   ```

5. **Ver logs:**
   ```bash
   docker compose -f docker-compose.prod.yml logs app
   ```

### Langgraph Development

Para usar langgraph en desarrollo:

1. **Conectarse al contenedor de la aplicación:**
   ```bash
   docker compose -f docker-compose.dev.yml exec app bash
   ```

2. **Ejecutar langgraph dentro del contenedor:**
   ```bash
   langgraph dev --host 0.0.0.0
   ```

Una vez iniciado, puedes acceder a la interfaz de Langgraph en:
- http://localhost:2024

### Detalles de los Contenedores
- Aplicación FastAPI: http://localhost:8000
- MongoDB (solo en desarrollo): mongodb://localhost:32768
- Langgraph UI (desarrollo): http://localhost:2024 (accesible después de ejecutar langgraph dev dentro del contenedor)

## Notes

- Vector storage uses MongoDB, ensure it is properly configured.
- Customize prompts and nodes in the `ai/` folder as needed.
- LangGraph CLI is optional but recommended for graph development and debugging.

## License

MIT
