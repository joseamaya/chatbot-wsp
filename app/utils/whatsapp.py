import os
import httpx

from app.database.models.message import Message
from app.database.models.message import MessageType


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
        media_content: Binary content for media messages (default: None)

    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    if not whatsapp_token or not whatsapp_phone_number_id:
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

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://graph.facebook.com/v22.0/{whatsapp_phone_number_id}/messages",
            headers=headers,
            json=json_data,
        )

    result = response.status_code == 200
    if result:
        outgoing_message = Message(
            chat=chat,
            content=response_text,
            message_type=MessageType.HUMAN if is_human else MessageType.AI,
            sender_id=sender_id if is_human else None
        )
        await outgoing_message.save()
    return result
