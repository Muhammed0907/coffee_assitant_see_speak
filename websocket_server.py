import asyncio
import websockets
import json
import threading
import time
from typing import Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserPresenceWebSocketServer:
    def __init__(self, host='192.168.2.42', port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.current_user_status = {
            'user_present': False,
            'user_count': 0,
            'last_detection_time': None,
            'distance': None,
            'gender': None,
            'age': None
        }
        self.server = None
        self.loop = None
        
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        # Send current status to new client
        await self.send_to_client(websocket, self.current_user_status)
        
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected: {websocket.remote_address}")
        
    async def send_to_client(self, websocket, data):
        """Send data to a specific client"""
        try:
            message = json.dumps(data)
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
            
    async def broadcast_to_all(self, data):
        """Broadcast data to all connected clients"""
        if not self.clients:
            return
            
        message = json.dumps(data)
        disconnected = set()
        
        for client in self.clients.copy():
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
        
    async def handle_client(self, websocket):
        """Handle WebSocket client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    await self.send_to_client(websocket, {
                        'error': 'Invalid JSON format'
                    })
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
            
    async def handle_client_message(self, websocket, data):
        """Handle messages from clients"""
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self.send_to_client(websocket, {
                'type': 'pong',
                'timestamp': time.time()
            })
        elif message_type == 'get_status':
            await self.send_to_client(websocket, {
                'type': 'status_update',
                **self.current_user_status
            })
        else:
            await self.send_to_client(websocket, {
                'error': f'Unknown message type: {message_type}'
            })
    
    def update_user_status(self, user_present=False, user_count=0, distance=None, gender=None, age=None):
        """Update user status and broadcast to all clients"""
        # Update status
        self.current_user_status.update({
            'user_present': user_present,
            'user_count': user_count,
            'last_detection_time': time.time() if user_present else self.current_user_status['last_detection_time'],
            'distance': distance,
            'gender': gender,
            'age': age
        })
        
        # Create broadcast message
        message = {
            'type': 'status_update',
            'timestamp': time.time(),
            **self.current_user_status
        }
        
        # Schedule broadcast in the event loop
        if self.loop and not self.loop.is_closed():
            try:
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_to_all(message), 
                    self.loop
                )
            except Exception as e:
                logger.error(f"Error scheduling broadcast: {e}")
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        
    def run_server(self):
        """Run the server in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.start_server())
            self.loop.run_forever()
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
        finally:
            if self.server:
                self.server.close()
            self.loop.close()
    
    def start(self):
        """Start the WebSocket server in a background thread"""
        self.thread = threading.Thread(target=self.run_server, daemon=True)
        self.thread.start()
        logger.info("WebSocket server thread started")
        
    def stop(self):
        """Stop the WebSocket server"""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)
        logger.info("WebSocket server stopped")

# Global instance for easy access
websocket_server = None

def init_websocket_server(host='localhost', port=8765):
    """Initialize the global WebSocket server"""
    global websocket_server
    websocket_server = UserPresenceWebSocketServer(host, port)
    websocket_server.start()
    return websocket_server

def update_user_presence(user_present=False, user_count=0, distance=None, gender=None, age=None):
    """Update user presence status (to be called from main application)"""
    global websocket_server
    if websocket_server:
        websocket_server.update_user_status(
            user_present=user_present,
            user_count=user_count,
            distance=distance,
            gender=gender,
            age=age
        )

if __name__ == "__main__":
    # Test server
    server = init_websocket_server()
    
    try:
        # Simulate user presence updates
        time.sleep(2)
        update_user_presence(True, 1, 1.5, 'M', 25)
        time.sleep(5)
        update_user_presence(False, 0)
        time.sleep(5)
        update_user_presence(True, 1, 2.0, 'F', 30)
        
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()