import json
from pathlib import Path
from datetime import datetime
from threading import Lock

DATA_DIR = Path("bot/storage/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

_file_lock = Lock()


def _chat_file(chat_id: int) -> Path:
    return DATA_DIR / f"{chat_id}.json"


def _default_chat(chat_id: int) -> dict:
    return {
        "chat_id": chat_id,
        "users": {},
        "meta": {
            "created_at": datetime.utcnow().isoformat()
        }
    }


def load_chat(chat_id: int) -> dict:
    file = _chat_file(chat_id)

    if not file.exists():
        return _default_chat(chat_id)

    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _default_chat(chat_id)

    data.setdefault("chat_id", chat_id)
    data.setdefault("users", {})
    data.setdefault("meta", {})
    data["meta"].setdefault("created_at", datetime.utcnow().isoformat())

    return data


def save_chat(chat_id: int, data: dict):
    file = _chat_file(chat_id)

    with _file_lock:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
