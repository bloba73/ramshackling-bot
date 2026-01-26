from storage.json_db import load_chat
from services.users import display_name

VALID_SORT_PARAMS = {
    "balance": lambda u: u.get("balance", 0),
    "games_played": lambda u: u.get("meta", {}).get("games_played", 0),
    "total_wins": lambda u: u.get("meta", {}).get("total_wins", 0),
    "total_losses": lambda u: u.get("meta", {}).get("total_losses", 0),
    "total_draws": lambda u: u.get("meta", {}).get("total_draws", 0),
    "max_amount_won": lambda u: u.get("meta", {}).get("max_amount_won", 0),
    "max_amount_lost": lambda u: u.get("meta", {}).get("max_amount_lost", 0)
}

def get_leaderboard(chat_id: int, limit: int = 10, sort_by: str = "balance") -> list[dict]:
    chat = load_chat(chat_id)
    users = chat.get("users", {})

    if sort_by not in VALID_SORT_PARAMS:
        sort_by = "balance"
    
    leaderboard = []
    for uid, u in users.items():
        leaderboard.append({
            "user_id": int(uid),
            "display_name": display_name(chat_id, int(uid)),
            sort_by: VALID_SORT_PARAMS[sort_by](u)
        })

    leaderboard.sort(key=lambda x: x[sort_by], reverse=True)
    return leaderboard[:limit]
