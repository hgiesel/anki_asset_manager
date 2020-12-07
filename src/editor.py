from aqt.gui_hooks import editor_did_init_left_buttons

from .models import open_asset_manager_menu
from .utils import add_assets, remove_cards


def on_assets(editor):
    editor.saveNow(lambda: _on_assets(editor))


def _on_assets(editor):
    open_asset_manager_menu(editor.parentWindow, editor.note.model())


def is_cards_button(button: str) -> bool:
    return "pycmd('cards');" in button


def add_assets_button(lefttopbtns, editor):
    if remove_cards.value:
        try:
            lefttopbtns.remove(next(filter(is_cards_button, lefttopbtns)))
        except StopIteration:
            # in case another add-on already removed/modified it
            pass

    if not add_assets.value:
        return

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
