from hashlib import sha1
from typing import Optional, Union, Literal, Tuple

from ..config_types import (
    ScriptSetting,
    ConcreteScript,
    ScriptInsertion,
    ScriptPosition,
    Fmt,
)
from ..lib.registrar import get_interface
from ..utils import version

from .condition_parser import get_condition_parser
from .groupify import groupify_script_data
from .indent import indent_lines
from .script_data import stringify_sd, merge_sd
from .package import package, package_for_external


def encapsulate_scripts(scripts, version, indent_size) -> str:
    pretext = '<div id="anki-am" data-name="Assets by ASSET MANAGER"'
    version_text = f' data-version="{version}"' if len(version) > 0 else ""

    top_delim = f"{pretext}{version_text}>"
    bottom_delim = "</div>"

    indented_scripts = [indent_lines(scc, indent_size) for scc in scripts]
    combined = [
        item
        for sublist in [[top_delim], indented_scripts, [bottom_delim]]
        for item in sublist
    ]

    return "\n".join(combined)


def gen_data_attributes(name: str, version: str):
    return f'data-name="{name}" data-version="{version}"'


# skip this script
def position_does_not_match(script, position: str) -> bool:
    return script.position != position and not (
        script.position in ["into_template", "external"]
        and position in ["question", "answer"]
    )


def get_script_and_code(
    script, model_name, cardtype_name, position
) -> Tuple[ConcreteScript, str]:
    script
    if isinstance(script, ConcreteScript):
        return (script, script.code)
    else:

        iface = get_interface(script.tag)

        return (
            iface.getter(
                script.id,
                script.storage,
            ),
            iface.generator(
                script.id,
                script.storage,
                model_name,
                cardtype_name,
                position,
            ),
        )


def stringify_setting(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
    cardtype_name: str,
    position: ScriptInsertion,
) -> str:
    the_parser = get_condition_parser(cardtype_name, position)
    script_data = []

    if not setting.enabled or setting.insert_stub:
        return script_data

    for script, code in map(
        lambda s: get_script_and_code(
            s,
            model_name,
            cardtype_name,
            position,
        ),
        setting.scripts,
    ):
        if (
            not script.enabled
            or len(code) == 0
            or position_does_not_match(script, position)
        ):
            continue

        needs_inject, conditions_simplified = the_parser(script.conditions)

        if not needs_inject:
            continue

        tag = gen_data_attributes(
            script.name,
            script.version,
        )

        if script.position == "external":
            filename = f"_am_{model_id}_{sha1(script.name.encode()).hexdigest()}.js"
            script_data.append(
                package_for_external(
                    tag, script.type, filename, code, conditions_simplified
                )
            )
        else:
            script_data.append(
                package(tag, script.type, script.label, code, conditions_simplified)
            )

    stringified = []
    groups = groupify_script_data(script_data)
    in_html = position in ["question", "answer"]

    for key, group in groups:
        if len(key) == 0:
            stringified.extend(
                [stringify_sd(sd, setting.indent_size, in_html) for sd in group]
            )
        else:
            stringified.append(
                stringify_sd(merge_sd(key, list(group)), setting.indent_size, in_html)
            )

    return stringified
