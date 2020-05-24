from aqt import QAction, mw

from .gui_config.custom.config import ConfigDialog
from .utils import find_addon_by_name

from .config import get_setting_from_notetype

def invoke_options():
    dialog = ConfigDialog(mw)
    # dialog.setupUi(get_settings(mw.col))

    return dialog.exec_()

def setup_menu_option():
    action = QAction('Script Manager Settings...', mw)
    action.triggered.connect(invoke_options)
    mw.form.menuTools.addAction(action)

def setup_addon_manager():
    mw.addonManager.setConfigAction(__name__, invoke_options)

from anki.hooks import wrap
from aqt.qt import QDialogButtonBox, qconnect

def onAssets(self):
    current_row = self.form.modelsList.currentRow()
    current_notetype = self.mm.get(self.models[current_row]['id'])
    current_setting = get_setting_from_notetype(current_notetype)

    dialog = ConfigDialog(self.mw)
    dialog.setupUi(current_notetype['id'], current_setting)
    dialog.exec_()

def init_asset_button(self):
    f = self.form
    box = f.buttonBox
    t = QDialogButtonBox.ActionRole
    b = box.addButton(_("Assets..."), t)
    qconnect(b.clicked, self.onAssets)

def setup_models_dialog():
    from aqt.models import Models
    Models.onAssets = onAssets
    Models.setupModels = wrap(Models.setupModels, init_asset_button, pos='after')
