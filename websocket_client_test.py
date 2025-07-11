#!/usr/bin/env python3
"""
Simple WebSocket client for testing the user presence server
"""
import asyncio
import websockets
import json
import time

class WebSocketClient:
    def __init__(self, url='ws://192.168.2.42:8765'):
        self.url = url
        self.websocket = None
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.url)
            print(f"✅ Connected to {self.url}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def send_message(self, message):
        """Send a message to the server"""
        if not self.websocket:
            print("❌ Not connected")
            return
        
        print(f"🔍 Debug: WebSocket state before send - {self.websocket.state}")
        try:
            json_msg = json.dumps(message)
            await self.websocket.send(json_msg)
            print(f"📤 Sent: {message}")
            print(f"🔍 Debug: WebSocket state after send - {self.websocket.state}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ Send failed - Connection closed: {e}")
            print(f"🔍 Debug: Close code: {e.code}, reason: {e.reason}")
        except Exception as e:
            print(f"❌ Send failed: {e}")
            print(f"🔍 Debug: WebSocket state - {self.websocket.state if self.websocket else 'None'}")
    
    async def listen_for_messages(self):
        """Listen for messages from server"""
        if not self.websocket:
            print("❌ Not connected")
            return
        
        print("🎧 Starting to listen for messages...")
        try:
            while True:
                try:
                    # Use timeout to prevent blocking forever
                    print("🔍 Debug: Waiting for message...")
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    print(f"🔍 Debug: Raw message received: {message}")
                    data = json.loads(message)
                    print(f"📥 Received: {data}")
                    
                    # Auto-respond to server pings with pong
                    if data.get('type') == 'ping':
                        print("🏓 Server sent ping, responding with pong...")
                        await self.send_message({"data": "pong"})
                        
                except asyncio.TimeoutError:
                    # No message received, continue listening
                    print("🔍 Debug: Timeout, continuing to listen...")
                    continue
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"🔌 Connection closed: {e}")
                    print(f"🔍 Debug: Connection close code: {e.code}, reason: {e.reason}")
                    break
        except asyncio.CancelledError:
            print("👋 Listening stopped (task was cancelled)")
        except Exception as e:
            print(f"❌ Listen error: {e}")
            print(f"🔍 Debug: WebSocket state when error occurred - {self.websocket.state if self.websocket else 'None'}")
    
    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Connection closed")

async def demo_client():
    """Demo function showing different message types"""
    client = WebSocketClient()
    
    # Connect
    if not await client.connect():
        return
    
    # Start listening in background
    listen_task = asyncio.create_task(client.listen_for_messages())
    
    # Send different types of messages
    messages = [
        # Ping test
        {"data": "ping"},
        
        # Get current status
        {"data": "get_status"},
        
        # Get server configuration
        {"data": "get_config"},
        
        # Send client info
        {"data": "client_info", "data": {"name": "Test Client", "version": "1.0"}},
        
        # Request immediate update
        {"data": "request_immediate_update"},
        
        # Change interval (uncomment to test)
        # {"data": "set_interval", "interval": 60},
    ]
    
    for i, msg in enumerate(messages):
        print(f"\n--- Test {i+1} ---")
        await client.send_message(msg)
        await asyncio.sleep(2)  # Wait for response
    
    # Wait a bit more to see any interval broadcasts
    print("\n--- Waiting for interval broadcasts (30 seconds) ---")
    await asyncio.sleep(30)
    
    # Cancel listening and close
    listen_task.cancel()
    await client.close()

async def interactive_client():
    """Interactive client for manual testing"""
    client = WebSocketClient()
    
    # Connect
    if not await client.connect():
        return
    
    # Start listening in background
    print("🚀 Starting listening task...")
    listen_task = asyncio.create_task(client.listen_for_messages())
    await asyncio.sleep(0.1)  # Give listening task a moment to start
    print("✅ Listening task started")
    
    print("\n🎮 Interactive WebSocket Client")
    print("Available commands:")
    print("  ping - Send ping to server")
    print("  server_ping - Request server to ping you")
    print("  status - Get status")
    print("  config - Get config")
    print("  info - Send client info")
    print("  update - Request immediate update")
    print("  interval X - Set interval to X seconds")
    print("  quit - Exit")
    
    try:
        while True:
            # Check if listening task is still alive
            if listen_task.done():
                print("⚠️ Listening task has stopped!")
                exception = listen_task.exception()
                if exception:
                    print(f"❌ Listening task error: {exception}")
            
            # Check WebSocket connection status
            if client.websocket and client.websocket.state.name in ['CLOSED', 'CLOSING']:
                print(f"⚠️ WebSocket connection is closed! State: {client.websocket.state}")
                break
            
            cmd = input("\n💬 Enter command: ").strip().lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'ping':
                await client.send_message({"data": "ping"})
            elif cmd == 'server_ping':
                await client.send_message({"data": "server_ping"})
            elif cmd == 'status':
                await client.send_message({"data": "get_status"})
            elif cmd == 'config':
                await client.send_message({"data": "get_config"})
            elif cmd == 'info':
                await client.send_message({
                    "data": "client_info", 
                    "data": {"name": "Interactive Client", "timestamp": time.time()}
                })
            elif cmd == 'update':
                await client.send_message({"data": "request_immediate_update"})
            elif cmd.startswith('interval '):
                try:
                    interval = int(cmd.split(' ')[1])
                    await client.send_message({"data": "set_interval", "interval": interval})
                except:
                    print("❌ Invalid interval format. Use: interval 30")
            else:
                print("❌ Unknown command")
    
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    
    # Cancel listening and close
    listen_task.cancel()
    await client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        # Run demo
        asyncio.run(demo_client())
    else:
        # Run interactive client
        asyncio.run(interactive_client())