from multiprocessing import managers
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@app.get("/")
def Home():
    return {"Welcome home"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    now = datetime.now()
    currency_time = now.strftime("%H:%M:$S")

    try:
        while True:
            data = await websocket.receive_text()
            message = {"time": currency_time, "client_id": client_id, "message": data}
            print("Broadcasting message:", message)  # Parse data as JSON
            await manager.broadcast(message)
    except WebSocketDisconnect:
    
        manager.disconnect(websocket)
        message = {"time": currency_time, "client_id": client_id, "message": "Offline"}
        await manager.broadcast(message)
