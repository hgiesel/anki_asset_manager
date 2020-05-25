from aqt import mw
from aqt.reviewer import Reviewer
from aqt.webview import WebContent

from ..config import maybe_get_setting_from_card

addon_package = mw.addonManager.addonFromModule(__name__)

def append_scripts(web_content: WebContent, context):
    if not isinstance(context, Reviewer):
        return

    maybe_sett = maybe_get_setting_from_card(context.card)

    if not maybe_sett:
        return

    web_content.css.append(
        f"/_addons/{addon_package}/web/my-addon.css")
    web_content.js.append(
        f"/_addons/{addon_package}/web/my-addon.js")

    web_content.head += "<script>console.log('my-addon')</script>"
    web_content.body += "<div id='my-addon'></div>"
