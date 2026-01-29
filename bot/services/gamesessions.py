from datetime import datetime
from threading import Lock

class GameSessionManager:
    def __init__(self):
        self._sessions = {}
        self._lock = Lock()

    def start(self, chat_id: int, user_id: int, game: str):
        key = (chat_id, user_id)

        with self._lock:
            if key in self._sessions:
                return False

            self._sessions[key] = {
                "game": game,
            }
            return True

    def get(self, chat_id: int, user_id: int):
        return self._sessions.get((chat_id, user_id))

    def end(self, chat_id: int, user_id: int):
        with self._lock:
            self._sessions.pop((chat_id, user_id), None)


game_sessions = GameSessionManager()
