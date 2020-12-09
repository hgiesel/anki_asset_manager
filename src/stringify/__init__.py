from typing import List
from dataclasses import replace

from ..config_types import ScriptSetting, Fmt
from ..utils import version
from ..lib.registrar import get_reducer

from .stringify import stringify_setting, encapsulate_scripts
from .prevent_reinclusion import get_prevent_reinclusion
from .condition_parser import get_condition_parser
from .groupify import groupify_external


def stringify_for_template(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
    cardtype_name: str,
    fmt: Fmt,
) -> str:
    stringified_scripts = stringify_setting(
        setting,
        model_name,
        model_id,
        cardtype_name,
        fmt,
    )

    if not setting.insert_stub and fmt == "question":
        stringified_scripts.insert(0, get_prevent_reinclusion(setting.indent_size))

    code_string = (
        encapsulate_scripts(
            stringified_scripts,
            version,
            setting.indent_size,
        )
        if setting.enabled
        else ""
    )

    return code_string


def stringify_for_head(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
    cardtype_name: str,
) -> str:
    return "\n".join(
        stringify_setting(
            setting,
            model_name,
            model_id,
            cardtype_name,
            "head",
        )
    )


def stringify_for_body(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
    cardtype_name: str,
) -> str:
    return "\n".join(
        stringify_setting(
            setting,
            model_name,
            model_id,
            cardtype_name,
            "body",
        )
    )


def stringify_for_external(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
) -> List[str]:
    stringified_scripts = []
    groups = groupify_external(setting.scripts)
    for key, group in groups:
        inner_setting = replace(setting, scripts=list(group))
        inner = stringify_setting(
            inner_setting,
            model_name,
            model_id,
            None,
            "external",
        )

        if len(inner) == 0:
            continue

        if len(key) == 0:
            stringified_scripts.extend(inner)
        else:
            reducer = get_reducer(key)
            stringified_scripts.append(reducer.reducer(inner))

    return stringified_scripts


__all__ = [
    stringify_for_template,
    stringify_for_head,
    stringify_for_body,
    stringify_for_external,
    get_condition_parser,
]
