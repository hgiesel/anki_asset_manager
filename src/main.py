from aqt import QAction, mw

from .gui_config.custom.am_config import AMConfigDialog
from .lib.config import get_settings

from .utils import find_addon_by_name

def invoke_options():
    dialog = AMConfigDialog(mw)
    dialog.setupUi(get_settings(mw.col))

    return dialog.exec_()

def setup_menu_option():
    action = QAction('Script Manager Settings...', mw)
    action.triggered.connect(invoke_options)
    mw.form.menuTools.addAction(action)

def setup_addon_manager():
    mw.addonManager.setConfigAction(__name__, invoke_options)
