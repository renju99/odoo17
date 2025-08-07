#!/usr/bin/env python3
"""
WebSocket Debug Script for Odoo 17
This script helps debug WebSocket connection issues by monitoring the connection
and providing detailed logging.
"""

import asyncio
import websockets
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('websocket_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class WebSocketDebugger:
    def __init__(self, server_url, db_name, user_id=None):
        self.server_url = server_url.replace('http', 'ws')
        self.db_name = db_name
        self.user_id = user_id
        self.websocket = None
        self.message_count = 0
        
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            # Construct WebSocket URL
            ws_url = f"{self.server_url}/websocket?version=17.0-1"
            logger.info(f"Connecting to WebSocket: {ws_url}")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(ws_url)
            logger.info("WebSocket connection established successfully")
            
            # Send subscription message
            await self.subscribe()
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            return False
    
    async def subscribe(self):
        """Send subscription message"""
        try:
            subscribe_message = {
                "event_name": "subscribe",
                "data": {
                    "channels": [f"bus.db.{self.db_name}"],
                    "last": 0
                }
            }
            
            await self.websocket.send(json.dumps(subscribe_message))
            logger.info(f"Sent subscription message: {subscribe_message}")
            
        except Exception as e:
            logger.error(f"Failed to send subscription: {e}")
    
    async def listen(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self.websocket:
                self.message_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Check for empty messages
                if not message or message.strip() == '':
                    logger.warning(f"[{timestamp}] Empty message received (count: {self.message_count})")
                    continue
                
                # Try to parse JSON
                try:
                    parsed_message = json.loads(message)
                    logger.info(f"[{timestamp}] Message {self.message_count}: {parsed_message}")
                except json.JSONDecodeError as e:
                    logger.error(f"[{timestamp}] Invalid JSON message {self.message_count}: {message}")
                    logger.error(f"JSON Error: {e}")
                
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"WebSocket connection closed: {e}")
        except Exception as e:
            logger.error(f"Error in WebSocket listener: {e}")
    
    async def run(self):
        """Main run method"""
        if await self.connect():
            await self.listen()
        else:
            logger.error("Failed to establish WebSocket connection")

async def main():
    """Main function"""
    # Configuration - adjust these values
    server_url = "http://localhost:8069"  # Your Odoo server URL
    db_name = "odoo17"  # Your database name
    
    debugger = WebSocketDebugger(server_url, db_name)
    await debugger.run()

if __name__ == "__main__":
    print("WebSocket Debug Script for Odoo 17")
    print("=" * 40)
    print("This script will:")
    print("1. Connect to the Odoo WebSocket endpoint")
    print("2. Subscribe to bus channels")
    print("3. Monitor and log all messages")
    print("4. Detect empty or malformed messages")
    print("=" * 40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDebug session interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")