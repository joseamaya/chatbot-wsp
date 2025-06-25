from fastapi import APIRouter, Request, Response, HTTPException
import logging
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from beanie import PydanticObjectId

from app.config.settings import get_settings
from app.ai import graph_builder
from app.utils.whatsapp import send_response
from app.database.models.bot import Bot

whatsapp_router = APIRouter(
    prefix="/whatsapp",
    tags=["whatsapp"]
)

settings = get_settings()
logger = logging.getLogger(__name__)


@whatsapp_router.api_route("/webhook/{bot_id}", methods=["GET", "POST"])
async def whatsapp_handler(bot_id: str, request: Request) -> Response:
    """Handles incoming messages and status updates from the WhatsApp Cloud API for specific bots.

    Args:
        bot_id: The ID of the bot to handle the message
        request: The incoming request with webhook data
    """
    try:
        bot = await Bot.get(PydanticObjectId(bot_id))
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        if not bot.is_active:
            raise HTTPException(status_code=400, detail="Bot is not active")

        if request.method == "GET":
            params = request.query_params
            if params.get("hub.verify_token") == bot.whatsapp_verify_token:
                return Response(content=params.get("hub.challenge"), status_code=200)
            return Response(content="Verification token mismatch", status_code=403)

        try:
            data = await request.json()
            change_value = data["entry"][0]["changes"][0]["value"]
            if "messages" in change_value:
                message = change_value["messages"][0]
                from_number = message["from"]
                session_id = f"{bot_id}:{from_number}"
                content = ""

                if message["type"] == "audio":
                    pass
                elif message["type"] == "image":
                    pass
                else:
                    content = message["text"]["body"]

                config = {
                    "configurable": {
                        "thread_id": session_id,
                        "chat_id": session_id,
                        "prompt": bot.prompt
                    }
                }

                async with AsyncMongoDBSaver.from_conn_string(
                    settings.MONGO_DB_URL,
                    db_name=settings.MONGO_DB_NAME
                ) as checkpointer:
                    graph = graph_builder.compile(checkpointer=checkpointer)

                    await graph.ainvoke(
                        {"messages": [HumanMessage(content=content)]},
                        config,
                    )
                    output_state = await graph.aget_state(config=config)

                response_message = output_state.values["messages"][-1].content
                success = await send_response(
                    from_number=from_number,
                    response_text=response_message,
                    message_type="text",
                    whatsapp_token=bot.whatsapp_token,
                    whatsapp_phone_number_id=bot.whatsapp_phone_number_id
                )

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

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid bot ID format")
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
