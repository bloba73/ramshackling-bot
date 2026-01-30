from games.roulette import get_roulette_handler
from games.coinflip import get_coinflip_callback_handler
from handlers.conversation.multi_lobby import get_multi_lobby_handler, get_multi_lobby_callbacks
from handlers.conversation.solo_lobby import get_solo_lobby_handler
from handlers.callbacks.menu import get_menu_callback_handler
from handlers.commands.menu import get_menu_handlers
from handlers.commands.common import get_common_handlers
from handlers.commands.profile import get_profile_handlers
from handlers.commands.auth import get_registration_handler, get_deleteaccount_handler
from handlers.commands.wallet import get_wallet_handlers

def load_handlers():
    handlers = []

    handlers.append(get_roulette_handler())
    handlers.append(get_coinflip_callback_handler())
    handlers.append(get_multi_lobby_handler())
    handlers.extend(get_multi_lobby_callbacks()) # Потворить игру?
    handlers.append(get_solo_lobby_handler())
    # TODO: handlers.extend(get_solo_lobby_callbacks()) - повторить игру?
    handlers.extend(get_menu_handlers())

    handlers.extend(get_common_handlers())
    handlers.extend(get_profile_handlers())
    handlers.extend(get_wallet_handlers())
    handlers.append(get_menu_callback_handler())
    handlers.append(get_registration_handler())
    handlers.append(get_deleteaccount_handler())
 
    return handlers
