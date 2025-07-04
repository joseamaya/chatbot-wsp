from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from pydantic import BaseModel
from app.database.models.operator import Operator
from app.database.models.chat import Chat
from app.utils.websocket import connection_manager
from app.utils.auth import get_current_operator
import logging

websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

logger = logging.getLogger(__name__)


@websocket_router.websocket("/operator/{operator_token}/notifications")
async def websocket_endpoint(
    websocket: WebSocket,
    operator_token: str,
):
    """
    Endpoint WebSocket para que los operadores reciban notificaciones
    de mensajes nuevos en chats donde han tomado el control.
    """
    try:
        # Validar el token y obtener el operador
        from jwt import decode, InvalidTokenError
        from app.utils.auth import SECRET_KEY, ALGORITHM

        try:
            payload = decode(operator_token, SECRET_KEY, algorithms=[ALGORITHM])
            operator_id = payload.get("sub")
            if not operator_id:
                await websocket.close(code=4001, reason="Invalid token")
                return

            operator = await Operator.get(operator_id)
            if not operator:
                await websocket.close(code=4001, reason="Operator not found")
                return

        except InvalidTokenError:
            await websocket.close(code=4001, reason="Invalid token")
            return

        # Aceptar la conexión y registrarla
        await connection_manager.connect(websocket, operator_id)

        try:
            # Mantener la conexión abierta y escuchar mensajes del cliente
            while True:
                data = await websocket.receive_text()
                # Podemos procesar mensajes del cliente si es necesario
                await connection_manager.send_personal_message(
                    {"type": "ack", "message": "Message received"},
                    websocket
                )
        except WebSocketDisconnect:
            # Eliminar la conexión cuando se cierre
            connection_manager.disconnect(websocket, operator_id)

    except Exception as e:
        logger.error(f"Error in websocket connection: {str(e)}")
        await websocket.close(code=1011, reason="Internal server error")


# Endpoint para enviar una notificación de prueba
@websocket_router.get("/test-notification/{operator_id}")
async def test_notification(
    operator_id: str,
    current_operator: Operator = Depends(get_current_operator)
):
    """
    Envía una notificación de prueba al operador especificado
    """
    await connection_manager.broadcast_to_operator(
        {
            "type": "test",
            "message": "This is a test notification"
        },
        operator_id
    )
    return {"status": "notification sent"}
