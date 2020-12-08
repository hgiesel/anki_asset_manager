from aqt import mw
from aqt.webview import AnkiWebView
from aqt.utils import showText

from anki.models import NoteType

from .common import write_model_template

from ..config_types import AnkiFmt


def minify_command(unminified: str) -> str:
    escaped = unminified.replace('"', '\\"').replace('\n', '\\n')
    return f'''
require("html-minifier-terser").minify(
    "{escaped}", {{
    collapseBooleanAttributes: true,
    collapseWhitespace: true,
    continueOnParseError: true,
    decodeEntities: true,
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
}})
'''

minifier = AnkiWebView(title="minify")
addon_package = mw.addonManager.addonFromModule(__name__)

minifier.stdHtml("", js=[
    f"/_addons/{addon_package}/web/htmlminifier.js",
])

def pass_minified_to_callback(
    template: NoteType,
    fmt: AnkiFmt,
    unminified_html: str,
) -> None:
    cmd = minify_command(unminified_html)
    minifier.evalWithCallback(cmd, lambda minified: write_model_template(template, fmt, minified))
