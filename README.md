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
   pip install -r requirements/dev.txt
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

## Notes

- Vector storage uses MongoDB, ensure it is properly configured.
- Customize prompts and nodes in the `ai/` folder as needed.
- LangGraph CLI is optional but recommended for graph development and debugging.

## License

MIT
