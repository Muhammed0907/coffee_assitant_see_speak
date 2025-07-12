#!/usr/bin/env python3
"""
Simple WebSocket client - just send messages and see responses
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://7ex30qo57151.vicp.fun:8765"
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected!")
        
        # Send your ping message
        message = {"data": "ping"}
        await websocket.send(json.dumps(message))
        print(f"📤 Sent: {message}")
        
        # Wait for response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"📥 Received: {data}")
        
        # Send another message
        message2 = {"data": "get_status"}
        await websocket.send(json.dumps(message2))
        print(f"📤 Sent: {message2}")
        
        # Wait for response
        response2 = await websocket.recv()
        data2 = json.loads(response2)
        print(f"📥 Received: {data2}")

if __name__ == "__main__":
    asyncio.run(test_websocket())