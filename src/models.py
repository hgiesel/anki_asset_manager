from aqt.qt import QDialogButtonBox, qconnect
from aqt.models import Models
from anki.hooks import wrap

from ..gui_config.config import ConfigDialog
from .config import get_setting_from_notetype, maybe_get_setting_from_card

def on_assets(models):
    current_row = models.form.modelsList.currentRow()
    current_notetype = models.mm.get(models.models[current_row].id)
    current_setting = get_setting_from_notetype(current_notetype)

    dialog = ConfigDialog(models.mw)

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
    qconnect(b.clicked, lambda: on_assets(self))

def setup_models_dialog():
    Models.setupModels = wrap(Models.setupModels, init_asset_button, pos='after')
