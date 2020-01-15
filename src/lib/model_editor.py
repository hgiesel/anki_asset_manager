import os
import io
import re
import base64
from json import dumps
from functools import reduce
from string import Template

from anki import media
from aqt import mw
from aqt.utils import showInfo

from .config import serialize_setting
from .utils import version_string

def setup_models(settings):
    for st in settings:
        model = mw.col.models.byName(st['modelName'])
        # setup_model(model, st)

def setup_model(model, setting):
    remove_model_template(model)
    update_model_template(model, setting)

def gen_data_attributes(name, version):
    return f'data-name="{name}" data-version="{version}"'

scripts_delim = '<!-- SCRIPTS MANAGED by SCRIPT MANAGER -->'
encapsulated_delim = f'\n\n{scripts_delim}\n'

def remove_model_template(model):
    for template in model['tmpls']:
        template['qfmt'] = re.sub(
            f'\n*{scripts_delim}.*',
            '',
            template['qfmt'],
            flags=re.MULTILINE | re.DOTALL,
        ).strip()

        template['afmt'] = re.sub(
            f'\n*{scripts_delim}.*',
            '',
            template['afmt'],
            flags=re.MULTILINE | re.DOTALL,
        ).strip()

def get_condition_parser(card, frontside):
    is_true = lambda v: type(v) == bool and v == True
    is_false = lambda v: type(v) == bool and v == False

    # [needscondection, newcondection]
    def parse_condition(cond) -> [bool, list]:
        if len(cond) == 0:
            # empty conditions
            return True, cond

        elif type(cond) == bool:
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

            if type(parsed_cond[1]) == bool:
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
                    frontside and cond[2] in ['front', 'question'] or
                    not frontside and cond[2] in ['back', 'answer']
                ):
                    return True, True

                else:
                    return False, False

            elif cond[1] == '!=':
                if (
                    frontside and cond[2] in ['back', 'answer'] or
                    not frontside and cond[2] in ['front', 'question']
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

    elif type(conds) == bool and conds:
        return 'true'

    elif type(conds) == bool and not conds:
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
    if (type(conditions) == bool and conditions) or len(conditions) == 0:
        return code

    else:
        return (
            f'if ({stringify_conds(conditions)}) {{\n' +
            '\n'.join([f'    {line}' for line in code.split('\n')]) +
            '\n}'
        )

def turn_script_to_string(scr):
    return (
        f'<script {scr["tag"]}>\n' +
        f'{wrap_code(scr["code"], scr["conditions"])}\n' +
        '</script>'
    )

def update_model_template(model, settings):
    for tmpl in model['tmpls']:
        cardtype_name = tmpl['name']

        front_scripts = []
        back_scripts = []

        front_parser = get_condition_parser(cardtype_name, True)
        back_parser = get_condition_parser(cardtype_name, False)

        for scr in [scr for scr in settings['scripts'] if scr['enabled']]:
            needs_front_inject, simplified_conditions_front = front_parser(scr['conditions'])

            if needs_front_inject:
                front_scripts.append({
                    'tag': gen_data_attributes(scr['name'], scr['version']),
                    'code': scr['code'],
                    'conditions': simplified_conditions_front,
                })

            needs_back_inject, simplified_conditions_back = back_parser(scr['conditions'])

            if needs_back_inject:
                back_scripts.append({
                    'tag': gen_data_attributes(scr['name'], scr['version']),
                    'code': scr['code'],
                    'conditions': simplified_conditions_back,
                })

        front_string = (encapsulated_delim + '\n\n'.join([
            turn_script_to_string(scr) for scr in front_scripts
        ])) if len(front_scripts) > 0 else ''

        back_string = (encapsulated_delim + '\n\n'.join([
            turn_script_to_string(scr) for scr in back_scripts
        ])) if len(back_scripts) > 0 else ''

        tmpl['qfmt'] += front_string
        tmpl['afmt'] += back_string

    # notify anki that models changed (for synchronization e.g.)
    mw.col.models.save(model, True)
