from aqt import mw

version = '2.0'

def find_addon_by_name(addon_name):
    for name in mw.addonManager.allAddons():
        if mw.addonManager.addonName(name) == addon_name:
            return name

    return None

def show(x):
    from aqt.utils import showInfo
    import html
    showInfo(repr(html.escape(x)))
