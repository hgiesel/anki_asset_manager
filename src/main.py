from aqt import mw
from aqt.utils import showInfo

from .gui_config.custom.config import ConfigDialog
from .config import get_setting_from_notetype, maybe_get_setting_from_card

def show_info():
    showInfo('To configure the functionality of this add-on, go to "Tools > Manage Note Types", select your note type, and click "Assets...".')

def setup_addon_manager():
    mw.addonManager.setConfigAction(__name__, show_info)

from anki.hooks import wrap
from aqt.qt import QDialogButtonBox, qconnect

def onAssets(self):
    current_row = self.form.modelsList.currentRow()
    current_notetype = self.mm.get(self.models[current_row]['id'])
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
    qconnect(b.clicked, self.onAssets)

def setup_models_dialog():
    from aqt.models import Models
    Models.onAssets = onAssets
    Models.setupModels = wrap(Models.setupModels, init_asset_button, pos='after')

def setup_webview_hook():
    pass

from aqt.reviewer import Reviewer
from aqt.webview import WebContent

from aqt.gui_hooks import webview_will_set_content

addon_package = mw.addonManager.addonFromModule(__name__)

def append_scripts(web_content: WebContent, context):
    if not isinstance(context, Reviewer):
        return

    maybe_sett = maybe_get_setting_from_card(context.card)

    if not maybe_sett:
        return

    web_content.css.append(
        f"/_addons/{addon_package}/web/my-addon.css")
    web_content.js.append(
        f"/_addons/{addon_package}/web/my-addon.js")

    web_content.head += "<script>console.log('my-addon')</script>"
    web_content.body += "<div id='my-addon'></div>"

    from aqt.utils import showInfo

    showInfo(str(dir(web_content)))
    showInfo(str(dir(context)))

    showInfo(str(context.card))

webview_will_set_content.append(append_scripts)

mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")

