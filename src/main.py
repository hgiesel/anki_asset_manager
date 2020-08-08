from aqt import mw
from aqt.gui_hooks import webview_will_set_content
from aqt.utils import showInfo # not for debugging

from .config import get_setting_from_notetype, maybe_get_setting_from_card

from .gui_config.custom.config import ConfigDialog
from .lib.webview_hook import append_scripts

def show_info():
    showInfo('To configure the functionality of this add-on, go to "Tools > Manage Note Types", select your note type, and click "Assets...".')

def setup_addon_manager():
    mw.addonManager.setConfigAction(__name__, show_info)

from anki.hooks import wrap
from aqt.qt import QDialogButtonBox, qconnect

def on_assets(self, _old):
    current_row = self.form.modelsList.currentRow()
    current_notetype = self.mm.get(self.models[current_row].id)
    current_setting = get_setting_from_notetype(current_notetype)

    dialog = ConfigDialog(self.mw)
    dialog.setupUi(
        current_notetype['id'],
        current_notetype['name'],
        current_setting,
    )

    dialog.exec_()

def init_asset_button(self):
    f = self.form
    box = f.buttonBox
    t = QDialogButtonBox.ActionRole
    b = box.addButton(_("Assets..."), t)
    qconnect(b.clicked, self.on_assets)

def setup_models_dialog():
    from aqt.models import Models

    Models.on_assets = on_assets # not overriding
    Models.setupModels = wrap(Models.setupModels, init_asset_button, pos='after')

def setup_webview_hook():
    webview_will_set_content.append(append_scripts)
    mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")
