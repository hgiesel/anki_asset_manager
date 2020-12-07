from aqt.gui_hooks import editor_did_init_left_buttons

from .models import open_asset_manager_menu


def on_assets(editor):
    editor.saveNow(lambda: _on_assets(editor))


def _on_assets(editor):
    open_asset_manager_menu(editor.parentWindow, editor.note.model())


def add_assets_button(lefttopbtns, editor):
    assets_button = editor.addButton(
        None,
        "assets",
        on_assets,
        "Manage assets for this note type.",
        "Assets...",
        disables=False,
        rightside=False,
    )

    lefttopbtns.append(assets_button)


def init_editor():
    editor_did_init_left_buttons.append(add_assets_button)
