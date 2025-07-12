#!/usr/bin/env python3
"""
WebSocket client example for monitoring user presence.
This demonstrates how to connect to the user presence WebSocket server and receive real-time updates.
"""

import asyncio
import websockets
import json
import time

class UserPresenceClient:
    def __init__(self, uri='ws://7ex30qo57151.vicp.fun:8765'):
        self.uri = uri
        self.websocket = None
        
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"Connected to {self.uri}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            print("Disconnected from server")
    
    async def send_message(self, message):
        """Send a message to the server"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
    
    async def listen_for_updates(self):
        """Listen for user presence updates"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")
        except Exception as e:
            print(f"Error listening for updates: {e}")
    
    async def handle_message(self, data):
        """Handle incoming messages from the server"""
        message_type = data.get('type')
        
        if message_type == 'status_update':
            await self.handle_status_update(data)
        elif message_type == 'pong':
            print("Received pong from server")
        elif 'error' in data:
            print(f"Server error: {data['error']}")
        else:
            print(f"Unknown message type: {data}")
    
    async def handle_status_update(self, data):
        """Handle user presence status updates"""
        user_present = data.get('user_present', False)
        user_count = data.get('user_count', 0)
        distance = data.get('distance')
        gender = data.get('gender')
        age = data.get('age')
        last_detection = data.get('last_detection_time')
        
        status = "PRESENT" if user_present else "ABSENT"
        print(f"\n--- User Status Update ---")
        print(f"Status: {status}")
        print(f"User Count: {user_count}")
        print(f"Distance: {distance:.2f}m" if distance else "Distance: -")
        print(f"Gender: {gender if gender else '-'}")
        print(f"Age: {age if age else '-'}")
        
        if last_detection:
            detection_time = time.strftime('%H:%M:%S', time.localtime(last_detection))
            print(f"Last Detection: {detection_time}")
        
        print("-------------------------")
    
    async def ping_server(self):
        """Send a ping to the server"""
        await self.send_message({'type': 'ping'})
    
    async def request_status(self):
        """Request current status from server"""
        await self.send_message({'type': 'get_status'})
    
    async def run(self):
        """Main client loop"""
        if not await self.connect():
            return
        
        # Request initial status
        await self.request_status()
        
        # Start listening for updates
        await self.listen_for_updates()

async def main():
    """Example usage of the WebSocket client"""
    client = UserPresenceClient()
    
    try:
        print("Starting user presence monitoring client...")
        print("Press Ctrl+C to exit")
        await client.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())