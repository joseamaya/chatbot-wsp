from typing import Dict, Set
import json
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Diccionario para almacenar conexiones por operador
        # {operator_id: set(websocket_connections)}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, operator_id: str):
        await websocket.accept()
        if operator_id not in self.active_connections:
            self.active_connections[operator_id] = set()
        self.active_connections[operator_id].add(websocket)

    def disconnect(self, websocket: WebSocket, operator_id: str):
        if operator_id in self.active_connections:
            self.active_connections[operator_id].discard(websocket)
            # Limpiar el diccionario si no hay más conexiones para este operador
            if not self.active_connections[operator_id]:
                del self.active_connections[operator_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast_to_operator(self, message: dict, operator_id: str):
        if operator_id in self.active_connections:
            disconnected_websockets = set()
            for websocket in self.active_connections[operator_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception:
                    # Marcar conexiones cerradas para eliminarlas después
                    disconnected_websockets.add(websocket)

            # Eliminar conexiones cerradas
            for websocket in disconnected_websockets:
                self.active_connections[operator_id].discard(websocket)


# Instancia global del gestor de conexiones
connection_manager = ConnectionManager()
