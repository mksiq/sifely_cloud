# token_manager.py
import json
import os
from .const import TOKEN_PATH

def save_token(token_data: dict):
    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f)

def load_token():
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH, "r") as f:
        return json.load(f)
