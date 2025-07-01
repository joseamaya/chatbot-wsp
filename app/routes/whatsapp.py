from fastapi import APIRouter, Request, Response, HTTPException
import logging
from datetime import datetime
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from beanie import PydanticObjectId

from app.config.settings import get_settings
from app.ai import graph_builder
from app.utils.whatsapp import send_response
from app.database.models.bot import Bot
from app.database.models.chat import Chat

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

                chat = await Chat.find_one(
                    {"phone_number": from_number, "bot.$id": PydanticObjectId(bot_id), "is_active": True}
                )
                if not chat:
                    chat = Chat(
                        phone_number=from_number,
                        bot=bot,
                        started_at=datetime.utcnow(),
                        last_interaction=datetime.utcnow()
                    )
                    await chat.save()

                    welcome_text = bot.welcome_message or "¡Hola! ¿En qué puedo ayudarte?"

                    basic_info = []
                    if bot.business_hours:
                        basic_info.append(f"🕒 Horario de atención: {bot.business_hours}")
                    if bot.address:
                        basic_info.append(f"📍 Dirección: {bot.address}")
                    if bot.phone:
                        basic_info.append(f"📞 Teléfono: {bot.phone}")

                    first_message = welcome_text
                    if basic_info:
                        first_message += "\n\n" + "\n\n".join(basic_info)

                    await send_response(
                        from_number=from_number,
                        response_text=first_message,
                        message_type="text",
                        whatsapp_token=bot.whatsapp_token,
                        whatsapp_phone_number_id=bot.whatsapp_phone_number_id
                    )

                    if bot.specialties and len(bot.specialties) > 0:
                        specialties_text = "✨ Especialidades:\n" + "\n• ".join([""] + bot.specialties)
                        await send_response(
                            from_number=from_number,
                            response_text=specialties_text,
                            message_type="text",
                            whatsapp_token=bot.whatsapp_token,
                            whatsapp_phone_number_id=bot.whatsapp_phone_number_id
                        )

                    if bot.payment_methods and len(bot.payment_methods) > 0:
                        payments_text = "💳 Formas de pago:\n" + "\n• ".join([""] + bot.payment_methods)
                        await send_response(
                            from_number=from_number,
                            response_text=payments_text,
                            message_type="text",
                            whatsapp_token=bot.whatsapp_token,
                            whatsapp_phone_number_id=bot.whatsapp_phone_number_id
                        )

                    if bot.prices and len(bot.prices) > 0:
                        prices_text = "💰 Precios:\n" + "\n• ".join([""] + bot.prices)
                        await send_response(
                            from_number=from_number,
                            response_text=prices_text,
                            message_type="text",
                            whatsapp_token=bot.whatsapp_token,
                            whatsapp_phone_number_id=bot.whatsapp_phone_number_id
                        )

                    social_media = []
                    if bot.website:
                        social_media.append(f"🌐 Web: {bot.website}")
                    if bot.facebook:
                        social_media.append(f"👥 Facebook: {bot.facebook}")
                    if bot.instagram:
                        social_media.append(f"📸 Instagram: {bot.instagram}")
                    if bot.tiktok:
                        social_media.append(f"📱 TikTok: {bot.tiktok}")

                    if social_media:
                        await send_response(
                            from_number=from_number,
                            response_text="📱 Redes sociales:\n" + "\n".join([""] + social_media),
                            message_type="text",
                            whatsapp_token=bot.whatsapp_token,
                            whatsapp_phone_number_id=bot.whatsapp_phone_number_id
                        )
                    success = True
                else:
                    chat.last_interaction = datetime.utcnow()
                    chat.messages_count += 1
                    await chat.save()

                    config = {
                        "configurable": {
                            "thread_id": str(chat.id),
                            "chat_id": str(chat.id),
                            "prompt": str(bot.prompt)
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