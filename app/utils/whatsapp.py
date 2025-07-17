import httpx
import logging

from app.database.models.message import Message
from app.database.models.message import MessageType

logger = logging.getLogger(__name__)

async def send_response(
    from_number: str,
    chat,
    response_text: str,
    message_type: str = "text",
    whatsapp_token: str = None,
    whatsapp_phone_number_id: str = None,
    is_human: bool = False,
    sender_id: str | None = None
) -> bool:
    """Send response to user via WhatsApp API.

    Args:
        from_number: The recipient's phone number
        response_text: The message to send
        message_type: The type of message (default: "text")
        whatsapp_token: The WhatsApp token for the specific bot
        whatsapp_phone_number_id: The WhatsApp phone number ID for the specific bot
        is_human: Whether the message is from a human operator
        sender_id: ID of the human sender if applicable

    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        if not whatsapp_token or not whatsapp_phone_number_id:
            logger.error("Missing WhatsApp credentials (token or phone_number_id)")
            return False

        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
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

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://graph.facebook.com/v22.0/{whatsapp_phone_number_id}/messages",
                headers=headers,
                json=json_data,
            )

            if response.status_code != 200:
                logger.error(
                    f"WhatsApp API error - Status: {response.status_code}, "
                    f"Response: {response.text}, Phone: {from_number}"
                )
                return False

        # Guardar el mensaje enviado en la base de datos
        try:
            outgoing_message = Message(
                chat=chat,
                content=response_text,
                message_type=MessageType.HUMAN if is_human else MessageType.AI,
                sender_id=sender_id if is_human else None
            )
            await outgoing_message.save()
        except Exception as db_error:
            logger.error(f"Error saving outgoing message to database: {db_error}")
            # No retornamos False aquí porque el mensaje sí se envió

        logger.info(f"Message sent successfully to {from_number}")
        return True

    except httpx.TimeoutException:
        logger.error(f"Timeout sending message to {from_number}")
        return False
    except httpx.RequestError as req_error:
        logger.error(f"Request error sending message to {from_number}: {req_error}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending message to {from_number}: {e}", exc_info=True)
        return False
