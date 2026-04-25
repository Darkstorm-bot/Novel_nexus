"""
WebSocket router for real-time updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json

from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        # story_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, story_id: str):
        await websocket.accept()
        if story_id not in self.active_connections:
            self.active_connections[story_id] = set()
        self.active_connections[story_id].add(websocket)
        logger.info(f"WebSocket connected for story {story_id}")
    
    def disconnect(self, websocket: WebSocket, story_id: str):
        if story_id in self.active_connections:
            self.active_connections[story_id].discard(websocket)
            if not self.active_connections[story_id]:
                del self.active_connections[story_id]
        logger.info(f"WebSocket disconnected for story {story_id}")
    
    async def broadcast_to_story(self, story_id: str, message: dict):
        """Broadcast a message to all connections for a story."""
        if story_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[story_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn, story_id)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    story_id: str = Query(None, alias="story_id")
):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, story_id or "global")
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type")
            payload = message.get("payload", {})
            
            logger.info(f"Received WebSocket message: {message_type}", payload=payload)
            
            # Echo back acknowledgment
            await manager.send_personal_message(
                {"type": "ack", "message_type": message_type, "status": "received"},
                websocket
            )
            
            # Handle pipeline control messages
            if message_type == "approve_phase":
                phase = payload.get("phase")
                logger.info(f"Phase approval requested: {phase}")
                # In a real implementation, this would trigger backend logic
            
            elif message_type == "reject_phase":
                phase = payload.get("phase")
                reason = payload.get("reason")
                logger.info(f"Phase rejection requested: {phase}, reason: {reason}")
            
            elif message_type == "request_update":
                # Send current state back to client
                await manager.send_personal_message(
                    {"type": "pipeline_update", "payload": {"status": "updated"}},
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, story_id or "global")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, story_id or "global")


# Helper function to send pipeline updates
async def send_pipeline_update(story_id: str, pipeline_data: dict):
    """Send pipeline update to all connected clients for a story."""
    await manager.broadcast_to_story(
        story_id,
        {
            "type": "pipeline_update",
            "payload": pipeline_data,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        }
    )


# Helper function to send story updates
async def send_story_update(story_id: str, story_data: dict):
    """Send story update to all connected clients for a story."""
    await manager.broadcast_to_story(
        story_id,
        {
            "type": "story_update",
            "payload": story_data,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        }
    )


# Helper function to send character updates
async def send_character_update(story_id: str, character_data: dict):
    """Send character update to all connected clients for a story."""
    await manager.broadcast_to_story(
        story_id,
        {
            "type": "character_update",
            "payload": character_data,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        }
    )
