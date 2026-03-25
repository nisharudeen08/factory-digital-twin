#!/usr/bin/env python3
"""
Run both FastAPI and Unity WebSocket bridge together.

This script starts both servers in the same asyncio event loop.
"""
import uvicorn
import asyncio
import socket
import os
from unity_bridge import bridge as unity_bridge

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

async def run_servers():
    """Run both FastAPI and the standalone WebSocket bridge for legacy local workflows."""
    ip = get_lan_ip()
    
    # Get ports from environment variables (Railway deployment)
    ws_port = int(os.environ.get("WS_PORT", 8765))
    api_port = int(os.environ.get("API_PORT", int(os.environ.get("PORT", 8000))))
    
    print("=" * 55)
    print("FACTORY DIGITAL TWIN SERVER STARTING...")
    print("=" * 55)
    print(f"  Health check : http://localhost:{api_port}/health")
    print(f"  Android URL  : http://{ip}:{api_port}")
    print(f"  Unity WS URL : ws://{ip}:{ws_port}")
    print("=" * 55)

    # Start Unity WebSocket bridge on the explicitly requested standalone port.
    unity_bridge.port = ws_port
    await unity_bridge.start()
    print("Unity WebSocket bridge started", flush=True)

    # Run FastAPI server
    config = uvicorn.Config(
        "api_server:app",
        host="0.0.0.0",
        port=api_port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # Run both concurrently
    await asyncio.gather(
        server.serve(),
    )

if __name__ == "__main__":
    asyncio.run(run_servers())
