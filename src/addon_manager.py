from aqt import mw
from aqt.utils import showInfo # not for debugging

def show_info():
    showInfo('To configure the functionality of this add-on, go to "Tools > Manage Note Types", select your note type, and click "Assets...".')

def setup_addon_manager():
    mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")
    mw.addonManager.setConfigAction(__name__, show_info)
