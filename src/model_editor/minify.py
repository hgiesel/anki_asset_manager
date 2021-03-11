from aqt.utils import tooltip
from aqt import mw

from .minifier import get_minifier, process_minifieds


def insert_minified(
    unminifieds,
    template_fmts,
    callback,
) -> None:
    tooltip("Started insertion of minified HTML")
    minifier = get_minifier(mw, template_fmts, callback)
    minifier.minify(unminifieds)


def insert_unminified(
    unminifieds,
    template_fmts,
    callback,
) -> None:
    process_minifieds(unminifieds, template_fmts, callback)
