import logging
import os

import uvicorn

logger = logging.getLogger("factory_digital_twin.server")


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    port = int(os.environ.get("PORT", 8000))
    logger.info("Starting Factory Digital Twin server on port %s", port)
    logger.info("REST endpoints share the same port; WebSocket path is /ws")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
    )


if __name__ == "__main__":
    main()
