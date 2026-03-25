import json
import os
from pathlib import Path

import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "factory_config.json"


def update():
    if not CONFIG_PATH.exists():
        print("Config file not found!")
        return

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    print(f"Sending config update for '{config['factory_name']}'...")
    response = requests.post(f"{BASE_URL}/config", json=config, timeout=30)
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    update()
