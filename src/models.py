from aqt.models import Models
from aqt.gui_hooks import models_did_init_buttons

from ..gui_config.config import ConfigDialog

from .config import (
    get_setting_from_notetype,
    get_html_setting_from_notetype,
)


def on_assets(models: Models) -> None:
    current_row = models.form.modelsList.currentRow()
    current_notetype = models.mm.get(models.models[current_row].id)

    dialog = ConfigDialog(models.mw)

    dialog.setupUi(
        current_notetype["id"],
        current_notetype["name"],
        get_html_setting_from_notetype(current_notetype),
        get_setting_from_notetype(current_notetype),
    )

    dialog.exec_()


def init_asset_button(buttons, models: Models):
    buttons.append(
        (
            _("Assets..."),
            lambda: on_assets(models),
        )
    )

    return buttons


def init_models_dialog():
    models_did_init_buttons.append(init_asset_button)
