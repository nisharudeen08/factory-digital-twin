#!/usr/bin/env python3
"""
Run the FastAPI server locally using the same single-port shape as Render.
"""
import logging
import os
import socket

import uvicorn

logger = logging.getLogger("factory_digital_twin.run_server")


def get_lan_ip():
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_client.connect(("8.8.8.8", 80))
        return socket_client.getsockname()[0]
    finally:
        socket_client.close()


if __name__ == "__main__":
    ip = get_lan_ip()
    api_port = int(os.environ.get("PORT", 8000))

    print("=" * 55)
    print("FACTORY DIGITAL TWIN SERVER STARTING...")
    print("=" * 55)
    print(f"  Health check : http://localhost:{api_port}/health")
    print(f"  Android URL  : http://{ip}:{api_port}")
    print(f"  Unity WS URL : ws://{ip}:{api_port}/ws")
    print("=" * 55)

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logger.info("Starting single-port local server on %s", api_port)
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=api_port,
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
