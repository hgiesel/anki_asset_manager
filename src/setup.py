from aqt import QAction, mw

from .gui_config.custom.sm_config import SMConfigDialog
from .lib.config import get_settings

from .utils import find_addon_by_name

def invoke_options():
    dialog = SMConfigDialog(mw)
    dialog.setupUi(get_settings())

    return dialog.exec_()

def setup_addon_manager():
    mw.addonManager.setConfigAction(__name__, invoke_options)

def setup_menu_option():
    action = QAction('Script Manager Settings...', mw)
    action.triggered.connect(invoke_options)
    mw.form.menuTools.addAction(action)
