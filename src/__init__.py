from .webview import setup_webview_hook
from .models import setup_models_dialog
from .addon_manager import setup_addon_manager

def setup():
    setup_webview_hook()
    setup_models_dialog()
    setup_addon_manager()
