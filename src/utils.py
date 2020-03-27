from aqt import mw

version = '1.1'

def find_addon_by_name(addon_name):
    for name in mw.addonManager.allAddons():
        if mw.addonManager.addonName(name) == addon_name:
            return name

    return None
