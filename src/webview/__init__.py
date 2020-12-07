from aqt.gui_hooks import webview_will_set_content

from aqt import mw
from aqt.reviewer import Reviewer
from aqt.webview import WebContent

from ..config import maybe_get_setting_from_card
from ..stringify import stringify_for_head, stringify_for_body


# addon_package = mw.addonManager.addonFromModule(__name__)


def append_scripts(web_content: WebContent, context):
    if not isinstance(context, Reviewer):
        return

    setting = maybe_get_setting_from_card(context.card)

    if not setting:
        return

    model_name = context.card.model()["name"]
    model_id = context.card.model()["id"]

    template_name = context.card.template()["name"]

    ## alternative approach, which would require creating as file and sourcing from web folder
    ## however it would have the same effect in practice
    # web_content.css.append(
    #     f"/_addons/{addon_package}/web/my-addon.css")
    # web_content.js.append(
    #     f"/_addons/{addon_package}/web/my-addon.js")

    web_content.head += stringify_for_head(
        setting,
        model_name,
        model_id,
        template_name,
    )

    web_content.body += stringify_for_body(
        setting,
        model_name,
        model_id,
        template_name,
    )


def init_webview():
    webview_will_set_content.append(append_scripts)
