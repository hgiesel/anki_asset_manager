from typing import Optional

from aqt import mw
from aqt.qt import QDialog
from aqt.utils import showInfo
from aqt.addons import AddonsDialog
from aqt.gui_hooks import addons_dialog_will_show

from .utils import add_assets, remove_cards
from .utils import version

from ..gui_config.settings import Settings


def save_settings(addassets: bool, removecards: bool) -> None:
    add_assets.value = addassets
    remove_cards.value = removecards


addons_current: Optional[AddonsDialog] = None


def show_settings():
    settings = Settings(addons_current, save_settings)
    settings.setupUi(version, add_assets.value, remove_cards.value)
    settings.exec_()


def save_addons_window(addons):
    global addons_current
    addons_current = addons


def init_addon_manager():
    mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")
    mw.addonManager.setConfigAction(__name__, show_settings)

    addons_dialog_will_show.append(save_addons_window)
