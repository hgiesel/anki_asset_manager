from anki.hooks import addHook

from .setup import setup_menu_option, setup_addon_manager

def init():
    addHook('profileLoaded', setup_menu_option)
    addHook('profileLoaded', setup_addon_manager)

init()
