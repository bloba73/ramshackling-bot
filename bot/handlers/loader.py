from handlers.callbacks.menu import get_menu_callback_handler
from handlers.commands.menu import get_menu_handlers
from handlers.commands.common import get_common_handlers
from handlers.commands.profile import get_profile_handlers
from handlers.commands.auth import get_registration_handler, get_deleteaccount_handler
from handlers.commands.wallet import get_wallet_handlers

def load_handlers():
    handlers = []

    handlers.append(get_menu_callback_handler())
    handlers.extend(get_menu_handlers())
    handlers.extend(get_common_handlers())
    handlers.extend(get_profile_handlers())
    handlers.extend(get_wallet_handlers())
    handlers.append(get_registration_handler())
    handlers.append(get_deleteaccount_handler())

    return handlers
