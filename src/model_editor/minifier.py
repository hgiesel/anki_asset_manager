from typing import List
import json

from aqt import mw
from aqt.webview import AnkiWebView
from aqt.utils import showInfo, showWarning, tooltip

from .common import write_model_template

# # DEBUG
# mw.mainLayout.addWidget(minifier, 1)
# mw.minifier = minifier


def minify_command(unminifieds: List[str]) -> str:
    escaped = (
        "["
        + (
            ",".join(
                [
                    '"' + unminified.replace('"', '\\"').replace("\n", "\\n") + '"'
                    for unminified in unminifieds
                ]
            )
        )
        + "]"
    )

    result = f"pycmd(`insertMinifieds::${{JSON.stringify({escaped}.map(html => minify(html, minifyOptions)))}}`)"
    return result


def process_minifieds(minifieds: List[str], template_fmts, callback):
    for index, minified in enumerate(minifieds):
        template, fmt = template_fmts[index]
        write_model_template(template, fmt, minified)

    callback()


def notify_minification(callback):
    def inner():
        tooltip("Finished insertion of minified HTML")
        callback()

    return inner


class Minifier(AnkiWebView):
    def __init__(
        self,
        parent,
        template_fmts,
        callback,
    ):
        AnkiWebView.__init__(self, parent=parent, title="minifier")
        self.set_bridge_command(self.bridge_cmd, parent)

        self.template_fmts = template_fmts
        self.callback = callback

    def bridge_cmd(self, cmd: str) -> None:
        if cmd.startswith("insertMinifieds"):
            _, code = cmd.split("::", 1)
            data = json.loads(code)
            process_minifieds(
                data, self.template_fmts, notify_minification(self.callback)
            )

    def minify(
        self,
        unminifieds,
    ) -> None:
        self.eval(
            """
var minify = require("html-minifier-terser").minify
var minifyOptions = {
    collapseBooleanAttributes: true,
    collapseWhitespace: true,
    continueOnParseError: true,
    decodeEntities: false,
    minifyCSS: true,
    minifyJS: true,
    processConditionalComments: true,
    removeAttributeQuotes: true,
    removeComments: true,
    removeEmptyAttributes: true,
    removeOptionalTags: true,
    removeRedundantAttributes: true,
    removeScriptTypeAttributes: true,
    removeStyleLinkTypeAttributes: true,
    removeTagWhitespace: true,
    sortAttributes: true,
    sortClassName: true,
    trimCustomFragments: true,
    useShortDoctype: true,
}"""
        )

        cmd = minify_command(unminifieds)
        self.eval(cmd)


def get_minifier(parent, template_fmts, callback) -> Minifier:
    minifier = Minifier(parent, template_fmts, callback)

    addon_package = mw.addonManager.addonFromModule(__name__)
    minifier.stdHtml(
        "",
        js=[
            f"/_addons/{addon_package}/web/htmlminifier.js",
        ],
    )

    return minifier
