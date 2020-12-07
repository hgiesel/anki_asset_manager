from .webview import init_webview
from .models import init_models_dialog
from .addon_manager import init_addon_manager
from .fields import init_fields
from .editor import init_editor


def setup():
    init_webview()
    init_models_dialog()
    init_addon_manager()
    init_fields()
    init_editor()
