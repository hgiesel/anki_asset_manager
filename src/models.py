from aqt.qt import QDialog
from aqt.models import Models
from aqt.gui_hooks import models_did_init_buttons

from ..gui_config.config import ConfigDialog

from .config import (
    write_setting,
    get_setting_from_notetype,
    get_html_setting_from_notetype,
)

from .model_editor import setup_model
from .media_writer import write_media


def write_back(model_id: int, html_data, script_data) -> None:
    write_setting(model_id, html_data, script_data)

    setup_model(model_id, html_data, script_data)
    write_media(model_id, script_data)


def save(model_id: int, html_data, script_data):
    write_setting(model_id, html_data, script_data)


def open_asset_manager_menu(parent_window: QDialog, note_type):
    dialog = ConfigDialog(parent_window, save, write_back)

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
