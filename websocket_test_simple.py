#!/usr/bin/env python3
"""
Simple WebSocket client that waits for responses
"""
import asyncio
import websockets
import json

async def test_ping():
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Test 1: Ping
            print("\n--- Test 1: Ping ---")
            await websocket.send(json.dumps({"data": "ping"}))
            print("📤 Sent: ping")
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data}")
            
            # Test 2: Get Status
            print("\n--- Test 2: Get Status ---")
            await websocket.send(json.dumps({"data": "get_status"}))
            print("📤 Sent: get_status")
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data}")
            
            # Test 3: Get Config
            print("\n--- Test 3: Get Config ---")
            await websocket.send(json.dumps({"data": "get_config"}))
            print("📤 Sent: get_config")
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data}")
            
            # Test 4: Set Interval
            print("\n--- Test 4: Set Interval ---")
            await websocket.send(json.dumps({"data": "set_interval", "interval": 15}))
            print("📤 Sent: set_interval to 15 seconds")
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data}")
            
            print("\n✅ All tests completed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ping())