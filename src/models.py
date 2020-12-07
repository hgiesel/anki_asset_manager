from aqt.qt import QDialog
from aqt.models import Models
from aqt.gui_hooks import models_did_init_buttons

from ..gui_config.config import ConfigDialog

from .config import (
    get_setting_from_notetype,
    get_html_setting_from_notetype,
)


def open_asset_manager_menu(parent_window: QDialog, note_type):
    dialog = ConfigDialog(parent_window)

    dialog.setupUi(
        note_type["id"],
        note_type["name"],
        get_html_setting_from_notetype(note_type),
        get_setting_from_notetype(note_type),
    )

    dialog.exec_()


def on_assets(models: Models) -> None:
    current_row = models.form.modelsList.currentRow()
    current_notetype = models.mm.get(models.models[current_row].id)
    open_asset_manager_menu(models.mw, current_notetype)


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
