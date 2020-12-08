from typing import List
import json

from aqt import mw
from aqt.webview import AnkiWebView
from aqt.utils import tooltip

from anki.models import NoteType

from .common import write_model_template

from ..config_types import AnkiFmt

import os


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

    return f"JSON.stringify({escaped}.map(html => minify(html, minifyOptions)))"


minifier = AnkiWebView(title="minify")
addon_package = mw.addonManager.addonFromModule(__name__)

minifier.stdHtml(
    "",
    js=[
        f"/_addons/{addon_package}/web/htmlminifier.js",
    ],
)

minifier.eval(
    """
const minify = require("html-minifier-terser").minify
const minifyOptions = {
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
}"""
)


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


def maybe_minify(
    unminifieds,
    template_fmts,
    callback,
) -> None:
    if True:
        tooltip("Started insertion of minified HTML")
        cmd = minify_command(unminifieds)
        minifier.evalWithCallback(
            cmd,
            lambda minifieds: process_minifieds(
                json.loads(minifieds), template_fmts, notify_minification(callback)
            ),
        )
    else:
        process_minifieds(unminifieds, template_fmts, callback)
