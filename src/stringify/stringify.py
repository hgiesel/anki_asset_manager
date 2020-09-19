from hashlib import sha1
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
    srcTag = f" src=\"{sd['src']}\"" if 'src' in sd else ''

    opening, closing = (
        f'<script {sd["tag"]}{srcTag}>',
        '</script>',
    ) if in_html else (
        f'// {sd["tag"]}',
        '',
    )

    wrapped_code = wrap_code(sd["code"], sd["conditions"])
    indented_code = indent_lines(wrapped_code, indent_size if in_html else 0)

    # avoid two empty new lines for external scripts
    opening, indented_code = (
        f'{opening}\n',
        f'{indented_code}\n',
    ) if len(indented_code) > 0 else (
        opening,
        ''
    )

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

def stringify_setting(
    setting: Setting,
    model_name: str,
    model_id: int,
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

        if not script_gotten.enabled:
            continue

        if (
            script_gotten.position != position and not (
                script_gotten.position in ['into_template', 'external'] and
                position in ['question', 'answer']
            )
        ):
            continue

        needs_inject, conditions_simplified = the_parser(script_gotten.conditions)

        if not needs_inject:
            continue

        tag = gen_data_attributes(
            script_gotten.name,
            script_gotten.version,
        )
        filename = f'_am_{model_id}_{sha1(script_gotten.name.encode()).hexdigest()}'

        code = (
            script_gotten.code
            if isinstance(script, ConcreteScript)
            else get_interface(script.tag).generator(
                script.id,
                script.storage,
                model_name,
                cardtype_name,
                position,
            )
        )

        sd = {
            'tag': tag,
            'src': filename,
            # no code or conditions, as they are present in external file
            'code': '',
            'conditions': [],
        } if script_gotten.position == 'external' and position in ['question', 'answer'] else {
            'tag': tag,
            'code': code,
            'conditions': conditions_simplified,
        }

        if len(code) == 0:
            continue

        if position == 'external':
            script_data.append((filename, stringify_script_data(sd, setting.indent_size, False)))
        else:
            script_data.append(stringify_script_data(sd, setting.indent_size, True))

    return script_data
