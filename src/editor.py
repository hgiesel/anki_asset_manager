from aqt.gui_hooks import editor_did_init

from .models import open_asset_manager_menu
from .utils import add_assets, remove_cards


def on_assets(editor):
    editor.saveNow(lambda: _on_assets(editor))


def _on_assets(editor):
    open_asset_manager_menu(editor.parentWindow, editor.note.note_type())


def is_cards_button(button: str) -> bool:
    return "pycmd('cards');" in button


linkname = "assetManagerDialog" 
def apply_buttons(editor):
    if linkname not in editor._links:
        editor._links[linkname] = on_assets

    if remove_cards.value:
        editor.web.eval("assetManagerGlobal.hideCardsButton();");

    if add_assets.value:
        editor.web.eval("assetManagerGlobal.addAssetsButton();");

def init_editor():
    editor_did_init.append(apply_buttons)
