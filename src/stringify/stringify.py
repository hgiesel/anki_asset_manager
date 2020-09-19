from typing import Optional, Union, Literal

from ..config_types import Setting, ConcreteScript, ScriptInsertion, ScriptPosition, Fmt
from ..utils import version

from ..lib.registrar import get_interface

from .condition_parser import get_condition_parser, stringify_conds

def wrap_code(code, conditions: Union[bool, list]):
    if ((type(conditions) is bool) and conditions) or len(conditions) == 0:
        return code

    else:
        main_code = '\n'.join([f'    {line}' for line in code.split('\n')])
        return f'if ({stringify_conds(conditions)}) {{\n{main_code}\n}}'

def indent(line, indentation):
    return indentation + line if len(line) > 0 else line

def indent_lines(text: str, indent_size: int) -> str:
    return '\n'.join([
        indent(line, indent_size * ' ')
        for line
        in text.split('\n')
    ])

def stringify_script_data(sd, indent_size: int, in_html: bool) -> str:
    opening = f'<script {sd["tag"]}>\n' if in_html else f'// {sd["tag"]}\n'
    closing = '</script>' if in_html else ''

    wrapped_code = wrap_code(sd["code"], sd["conditions"])
    indented_code = indent_lines(wrapped_code, indent_size if in_html else 0) + '\n'

    return (
        opening +
        indented_code +
        closing
    )

def encapsulate_scripts(scripts, version, indent_size) -> str:
    pretext = "<div id=\"anki-am\" data-name=\"Assets by ASSET MANAGER\""
    version_text = f" data-version=\"{version}\"" if len(version) > 0 else ''

    top_delim = f"{pretext}{version_text}>"
    bottom_delim = '</div>'

    indented_scripts = [
        indent_lines(scc, indent_size)
        for scc in scripts
    ]
    combined = [
        item
        for sublist
        in [[top_delim], indented_scripts, [bottom_delim]]
        for item
        in sublist
    ]

    return '\n'.join(combined)

def gen_data_attributes(name: str, version: str):
    return f'data-name="{name}" data-version="{version}"'

####################### stringify functions

def stringify_setting(
    setting: Setting,
    model_name: str,
    cardtype_name: str,
    position: ScriptInsertion,
) -> str:
    the_parser = get_condition_parser(cardtype_name, position)
    script_data = []

    if not setting.enabled or setting.insert_stub:
        return script_data

    for script in setting.scripts:
        script_gotten = (
            script
            if isinstance(script, ConcreteScript)
            else get_interface(script.tag).getter(
                script.id,
                script.storage,
            )
        )

        if (
            script_gotten.enabled and
            script_gotten.position == ('into_template' if position in ['question', 'answer'] else position)
        ):
            needs_inject, conditions_simplified = the_parser(script_gotten.conditions)

            if needs_inject:
                sd = {
                    'tag': gen_data_attributes(
                        script_gotten.name,
                        script_gotten.version,
                    ),
                    'code': (
                        script_gotten.code
                        if isinstance(script, ConcreteScript)
                        else get_interface(script.tag).generator(
                            script.id,
                            script.storage,
                            model_name,
                            cardtype_name,
                            position,
                        )
                    ),
                    'conditions': conditions_simplified,
                }

                if len(sd['code']) > 0:
                    script_data.append(sd)

    stringified_scripts = [
        stringify_script_data(sd, setting.indent_size, True)
        for sd
        in script_data
    ]

    return stringified_scripts

prevent_reinclusion = {
    'tag': gen_data_attributes('Prevent reinclusion', 'v0.1'),
    'code': """
var ankiAms = document.querySelectorAll('#anki-am')
  if (ankiAms.length > 1) {
    for (const am of Array.from(ankiAms).slice(0, -1)) {
      am.outerHTML = ''
  }
}""".strip(),
    'conditions': [],
}
