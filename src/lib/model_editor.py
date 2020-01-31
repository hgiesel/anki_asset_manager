import os
import io
import re
import base64
from json import dumps
from functools import reduce
from string import Template

from anki import media
from aqt import mw

from .registrar import get_interface
from .types import SMConcrScript
from .config import serialize_setting
from .utils import version_string

def setup_models(settings):
    for st in settings:
        model = mw.col.models.byName(st.model_name)
        setup_model(model, st)

def setup_model(model, setting):
    needs_saving = False

    for template in model['tmpls']:
        for fmt in ['qfmt', 'afmt']:
            did_insert = update_model_template(
                template, fmt,
                get_model_template(setting, template['name'], fmt),
            )

            needs_saving = needs_saving or did_insert

    # notify anki that models changed (for synchronization e.g.)
    if needs_saving:
        mw.col.models.save(model, True)

def gen_data_attributes(name, version):
    return f'data-name="{name}" data-version="{version}"'

def get_template_slice(t):
    try:
        startpos_regex = re.compile(r'\n?\n? *?<div.*?id="anki\-sm".*?>', re.MULTILINE)
        endpos_regex = re.compile(r'</div> *?$', re.MULTILINE)

        startpos = re.search(startpos_regex, t)
        endpos = re.search(endpos_regex, t[startpos.end():])

        startpos_actual = startpos.start()
        endpos_actual = startpos.end() + endpos.end()

        return (startpos_actual, endpos_actual)

    except AttributeError:
        return None

def get_new_template(slice, old_template: str, scripts: str) -> str:
    sep_scripts = '\n\n' + scripts

    return (
        sep_scripts.join([
            old_template[:slice[0]],
            old_template[slice[1]:],
        ]) if slice
        else f'{old_template}{sep_scripts}' if len(scripts) > 0
        else None
    )

def update_model_template(template: object, fmt: str, scripts: str) -> bool:
    slice = get_template_slice(template[fmt])
    new_template = get_new_template(slice, template[fmt], scripts)

    if new_template:
        template[fmt] = new_template
        return True

    return False

def get_condition_parser(card, side):
    is_true = lambda v: isinstance(v, bool) and v == True
    is_false = lambda v: isinstance(v, bool) and v == False

    # [needscondection, newcondection]
    def parse_condition(cond) -> [bool, list]:
        if len(cond) == 0:
            # empty conditions
            return True, cond

        elif isinstance(cond, bool):
            return cond, cond

        elif cond[0] == '&':
            parsed_conds = [parse_condition(i) for i in cond[1:]]
            truth_result = reduce(lambda x, y: x and y, [res[0] for res in parsed_conds])
            parsed_result = [res[1] for res in parsed_conds]

            if any([is_false(pr) for pr in parsed_result]):
                # and condition contains False
                result = False
            else:
                # filter out False
                result = list(filter(lambda v: not is_true(v), parsed_result))
                if len(result) > 1:
                    # reinsert "&"
                    result.insert(0, cond[0])
                else:
                    # flatten list, drop "&"
                    result = [item for sublist in result for item in sublist]

            return truth_result, result

        elif cond[0] == '|':
            parsed_conds = [parse_condition(i) for i in cond[1:]]
            truth_result =  reduce(lambda x, y: x or y, [res[0] for res in parsed_conds])
            parsed_result = [res[1] for res in parsed_conds]

            if any([is_true(pr) for pr in parsed_result]):
                # or condition contains True
                result = True
            else:
                # filter out True
                result = list(filter(lambda v: not is_false(v), parsed_result))
                if len(result) > 1:
                    result.insert(0, cond[0])
                else:
                    result = [item for sublist in result for item in sublist]

            return truth_result, result

        elif cond[0] == '!':
            parsed_cond = parse_condition(cond[1])

            if isinstance(parsed_cond[1], bool):
                return True, not parsed_cond[1]
            else:
                return True, [cond[0], parsed_cond[1]]

        elif cond[0] == 'card':
            if cond[1] == '=':
                val = card == cond[2]

            elif cond[1] == '!=':
                val = card != cond[2]

            elif cond[1] == 'includes':
                val = cond[2] in card

            elif cond[1] == 'startsWith':
                val = card.startswith(cond[2])

            elif cond[1] == 'endsWith':
                val = card.endswith(cond[2])

            return val, val

        elif cond[0] == 'side':
            if cond[1] == '=':
                if (
                    side == 'qfmt' and cond[2] in ['front', 'question', 'qfmt'] or
                    side == 'afmt' and cond[2] in ['back', 'answer', 'afmt']
                ):
                    return True, True

                else:
                    return False, False

            elif cond[1] == '!=':
                if (
                    side == 'qfmt' and cond[2] in ['back', 'answer', 'afmt'] or
                    side == 'afmt' and cond[2] in ['front', 'question', 'qfmt']
                ):
                    return True, True

                else:
                    return False, False

        elif cond[0] == 'tag' or cond[0] == 'tagFull' or cond[0] == 'iter':
            return True, cond

    return parse_condition

def stringify_conds(conds) -> str:
    if len(conds) == 0:
        return 'true'

    elif isinstance(conds, bool) and conds:
        return 'true'

    elif isinstance(conds, bool) and not conds:
        return 'false'

    elif conds[0] == '&':
        stringified_conds = [stringify_conds(c) for c in conds[1:]]
        parsed_result = [res[1] for res in stringified_conds]
        if 'false' in parsed_result:
            return 'false'
        else:
            return ' && '.join([p for p in parsed_result if p != 'true'])

    elif conds[0] == '|':
        stringified_conds = [stringify_conds(c) for c in conds[1:]]
        parsed_result = [res[1] for res in stringified_conds]
        if 'true' in parsed_result:
            return 'true'
        else:
            return ' || '.join([p for p in parsed_result if p != 'false'])

    elif conds[0] == '!':
        stringed_cond = stringify_conds(conds[1])

        if stringed_cond == 'false':
            return 'true'
        elif stringed_cond == 'true':
            return 'false'
        else:
            return f'!({stringed_cond})'

    elif conds[0] == 'card':
        if conds[1] == '=':
            return f"'{{{{Card}}}}' === {conds[2]}"

        elif conds[1] == '!=':
            return f"'{{{{Card}}}}' === {conds[2]}"

        elif conds[1] == 'includes':
            return f"'{{{{Card}}}}'.includes('{conds[2]}')"

        elif conds[1] == 'startsWith':
            return f"'{{{{Card}}}}'.startsWith('{conds[2]}')"

        elif conds[1] == 'endsWith':
            return f"'{{{{Card}}}}'.endsWith('{conds[2]}')"

    elif conds[0] == 'tagString':
        if conds[1] == '=':
            return f"'{{{{Tags}}}}' === {conds[2]}"

        elif conds[1] == '!=':
            return f"'{{{{Tags}}}}' === {conds[2]}"

        elif conds[1] == 'includes':
            return f"'{{{{Tags}}}}'.includes('{conds[2]}')"

        elif conds[1] == 'startsWith':
            return f"'{{{{Tags}}}}'.startsWith('{conds[2]}')"

        elif conds[1] == 'endsWith':
            return f"'{{{{Tags}}}}'.endsWith('{conds[2]}')"

    elif conds[0] == 'tag':
        if conds[1] == '=':
            return f"'{{{{Tags}}}}'.split(' ').includes('{conds[2]}')"

        elif conds[1] == '!=':
            return f"'!{{{{Tags}}}}'.split(' ').includes('{conds[2]}')"

        elif conds[1] == 'includes':
            return f"'{{{{Tags}}}}'.split(' ').some(v => v.includes('{conds[2]}'))"

        elif conds[1] == 'startsWith':
            return f"'{{{{Tags}}}}'.split(' ').some(v => v.startsWith('{conds[2]}'))"

        elif conds[1] == 'endsWith':
            return f"'{{{{Tags}}}}'.split(' ').some(v => v.endsWith('{conds[2]}'))"

def wrap_code(code, conditions):
    if (isinstance(conditions, bool) and conditions) or len(conditions) == 0:
        return code

    else:
        return (
            f'if ({stringify_conds(conditions)}) {{\n' +
            '\n'.join([f'    {line}' for line in code.split('\n')]) +
            '\n}'
        )

def indent(line, indentation):
    return indentation + line if len(line) > 0 else line

def indent_lines(text, indent_size):
    return '\n'.join([
        indent(line, indent_size * ' ')
        for line
        in text.split('\n')
    ])

def turn_script_to_string(scr, indent_size):
    return (
        f'<script {scr["tag"]}>\n' +
        f'{indent_lines(wrap_code(scr["code"], scr["conditions"]), indent_size)}\n' +
        '</script>'
    )

def encapsulate_scripts(scripts, version, indent_size) -> str:
    pretext = "<div id=\"anki-sm\" data-name=\"SCRIPTS managed by SCRIPT MANAGER\""
    version_text = f" data-version=\"{version}\"" if len(version) > 0 else ''

    top_delim = f"{pretext}{version_text}>"
    bottom_delim = '</div>'

    indented_scripts = [indent_lines(scc, indent_size) for scc in scripts]
    combined = [
        item
        for sublist
        in [[top_delim], indented_scripts, [bottom_delim]]
        for item
        in sublist
    ]

    return '\n'.join(combined)

def get_model_template(setting, cardtype_name, fmt) -> (str, str):
    the_scripts = []
    the_parser = get_condition_parser(cardtype_name, fmt)

    if setting.enabled and not setting.insert_stub:
        for scr in setting.scripts:
            the_scr = scr if isinstance(scr, SMConcrScript) else get_interface(scr.tag).getter(scr.id, scr.storage)

            if the_scr.enabled:
                needs_inject, simplified_conditions = the_parser(the_scr.conditions)

                if needs_inject:
                    fs = {
                        'tag': gen_data_attributes(the_scr.name, the_scr.version),
                        'code': (
                            the_scr.code
                            if isinstance(scr, SMConcrScript)
                            else get_interface(scr.tag).generator(scr.id, scr.storage, setting.model_name, cardtype_name, fmt)
                        ),
                        'conditions': simplified_conditions,
                    }

                    the_scripts.append(fs)

    code_string = encapsulate_scripts(
        [turn_script_to_string(scr, setting.indent_size) for scr in the_scripts],
        version_string,
        setting.indent_size,
    ) if setting.enabled else ''

    return code_string
