import os

import httpx
from fastapi import APIRouter, Request, Response
import logging

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver

from app.config.settings import get_settings
from app.ai import graph_builder

whatsapp_router = APIRouter(
    prefix="/whatsapp",
    tags=["whatsapp"]
)

settings = get_settings()

logger = logging.getLogger(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

async def send_response(
    from_number: str,
    response_text: str,
    message_type: str = "text",
    media_content: bytes = None,
) -> bool:
    """Send response to user via WhatsApp API."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    json_data = {}
    if message_type == "text":
        json_data = {
            "messaging_product": "whatsapp",
            "to": from_number,
            "type": "text",
            "text": {"body": response_text},
        }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages",
            headers=headers,
            json=json_data,
        )

    return response.status_code == 200

@whatsapp_router.api_route("/whatsapp_response", methods=["GET", "POST"])
async def whatsapp_handler(request: Request) -> Response:
    """Handles incoming messages and status updates from the WhatsApp Cloud API."""

    if request.method == "GET":
        params = request.query_params
        if params.get("hub.verify_token") == os.environ.get("WHATSAPP_VERIFY_TOKEN"):
            return Response(content=params.get("hub.challenge"), status_code=200)
        return Response(content="Verification token mismatch", status_code=403)

    try:
        data = await request.json()
        change_value = data["entry"][0]["changes"][0]["value"]
        if "messages" in change_value:
            message = change_value["messages"][0]
            from_number = message["from"]
            session_id = from_number
            content = ""
            if message["type"] == "audio":
                pass
            elif message["type"] == "image":
                pass
            else:
                content = message["text"]["body"]

            async with AsyncMongoDBSaver.from_conn_string(
                settings.MONGO_DB_URL,
                db_name=settings.MONGO_DB_NAME
            ) as checkpointer:
                graph = graph_builder.compile(checkpointer=checkpointer)
                await graph.ainvoke(
                    {"messages": [HumanMessage(content=content)]},
                    {"configurable": {"thread_id": session_id}, "chat_id": session_id},
                )
                output_state = await graph.aget_state(config={"configurable": {"thread_id": session_id}})

            response_message = output_state.values["messages"][-1].content
            success = await send_response(from_number, response_message, "text")

            if not success:
                return Response(content="Failed to send message", status_code=500)

            return Response(content="Message processed", status_code=200)

        elif "statuses" in change_value:
            return Response(content="Status update received", status_code=200)

        else:
            return Response(content="Unknown event type", status_code=400)

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return Response(content="Internal server error", status_code=500)