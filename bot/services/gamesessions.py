from datetime import datetime
from threading import Lock
from typing import Optional, Dict, Tuple

class GameSessionManager:
    def __init__(self):
        # key = (chat_id, owner_id)
        self._sessions: Dict[Tuple[int, int], dict] = {}
        self._lock = Lock()

    def start(
        self,
        chat_id: int,
        owner_id: int,
        game: str,
        *,
        mode: str = "solo",
    ) -> bool:
        key = (chat_id, owner_id)

        with self._lock:
            if key in self._sessions:
                return False

            self._sessions[key] = {
                "game": game,
                "mode": mode, # solo | duel
                "owner_id": owner_id,
                "created_at": datetime.utcnow(),

                "bet": None,
                "players": [owner_id],
                "message_id": None,
                "state": "created", # created | waiting | started
            }
            return True

    def get(self, chat_id: int, owner_id: int) -> Optional[dict]:
        return self._sessions.get((chat_id, owner_id))

    def has_active(self, chat_id: int, user_id: int) -> bool:
        with self._lock:
            for session in self._sessions.values():
                if user_id in session.get("players", []):
                    return True
        return False

    def add_player(self, chat_id: int, owner_id: int, user_id: int) -> bool:
        with self._lock:
            session = self._sessions.get((chat_id, owner_id))
            if not session:
                return False

            if user_id in session["players"]:
                return False

            session["players"].append(user_id)
            return True

    def set_bet(self, chat_id: int, owner_id: int, bet: int):
        with self._lock:
            session = self._sessions.get((chat_id, owner_id))
            if session:
                session["bet"] = bet

    def set_message(self, chat_id: int, owner_id: int, message_id: int):
        with self._lock:
            session = self._sessions.get((chat_id, owner_id))
            if session:
                session["message_id"] = message_id

    def set_state(self, chat_id: int, owner_id: int, state: str):
        with self._lock:
            session = self._sessions.get((chat_id, owner_id))
            if session:
                session["state"] = state

    def end(self, chat_id: int, owner_id: int):
        with self._lock:
            self._sessions.pop((chat_id, owner_id), None)


game_sessions = GameSessionManager()
