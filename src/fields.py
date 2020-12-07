import re
from dataclasses import replace

from aqt.gui_hooks import fields_did_rename_field, fields_did_delete_field
from aqt.utils import showText
from aqt.fields import FieldDialog

from .config_types import ConcreteHTML

from .config import (
    write_html,
    get_html_setting_from_notetype,
)


def make_pattern(tag_name: str) -> str:
    return r'\{\{([#/^]?)' + re.escape(tag_name) + r'\}\}'


def replace_reference(text: str, old: str, new: str) -> str:
    return re.sub(make_pattern(old), f"{{{{\\1{new}}}}}", text)


def delete_reference(text: str, old: str) -> str:
    return re.sub(make_pattern(old), "", text)


def rename_in_assets(fields, field, old_name: str):
    html = get_html_setting_from_notetype(fields.model)

    if not html.enabled:
        return

    new_html = replace(
        html,
        fragments=[
            replace(fragment, code=replace_reference(fragment.code, old_name, field["name"]))
            for fragment
            in html.fragments
        ],
    )

    write_html(new_html, custom_model=fields.model)


def delete_in_assets(fields, field):
    html = get_html_setting_from_notetype(fields.model)

    if not html.enabled:
        return

    new_html = replace(
        html,
        fragments=[
            replace(fragment, code=delete_reference(fragment.code, field["name"]))
            for fragment
            in html.fragments
        ],
    )

    write_html(new_html, custom_model=fields.model)


def init_fields():
    fields_did_rename_field.append(rename_in_assets)
    fields_did_delete_field.append(delete_in_assets)
