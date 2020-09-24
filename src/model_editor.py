import os
import io
import re
import base64

from typing import Optional, Tuple, List
from json import dumps
from string import Template

from anki import media
from aqt import mw

from .config import get_setting_from_notetype
from .config_types import AnkiFmt, Fmt, HTML, HTMLSetting, ScriptSetting

from .stringify import stringify_setting_for_template
from .stringify.condition_parser import get_condition_parser


startpos_regex = re.compile(r'\n?\n? *?<div.*?id="anki\-am".*?>', re.MULTILINE)
endpos_regex = re.compile(r'</div> *?$', re.MULTILINE)

def get_template_slice(t) -> Optional[Tuple[int, int]]:
    try:
        startpos = re.search(startpos_regex, t)
        endpos = re.search(endpos_regex, t[startpos.end():])

        startpos_actual = startpos.start()
        endpos_actual = startpos.end() + endpos.end()

        return (startpos_actual, endpos_actual)

    except AttributeError:
        return None

def get_new_template(slice: Optional[Tuple[int, int]], old_template: str, script_string: str) -> Optional[str]:
    sep_scripts = '\n\n' + script_string

    return (
        sep_scripts.join([
            old_template[:slice[0]],
            old_template[slice[1]:],
        ]) if slice
        else f'{old_template}{sep_scripts}' if len(script_string) > 0
        else None
    )

def update_model_template(template: object, fmt: AnkiFmt, script_string: str) -> bool:
    slice = get_template_slice(template[fmt])
    new_template = get_new_template(slice, template[fmt], script_string)

    if new_template:
        write_model_template(template, fmt, new_template)
        return True

    return False

def write_model_template(template: object, fmt: AnkiFmt, value: str) -> bool:
    template[fmt] = value

def setup_with_only_scripts(model_id: int, scripts: ScriptSetting):
    needs_saving = False
    model = mw.col.models.get(model_id)

    for template in model['tmpls']:
        # anki uses qfmt and afmt in model objects
        # I use question and answer
        for fmt in ['qfmt', 'afmt']:
            did_insert = update_model_template(
                template,
                fmt,
                stringify_setting_for_template(
                    scripts,
                    model['name'],
                    model_id,
                    template['name'],
                    'question' if fmt == 'qfmt' else 'answer',
                ),
            )

            needs_saving = needs_saving or did_insert

    # notify anki that models changed (for synchronization e.g.)
    if needs_saving:
        mw.col.models.save(model, True)

def find_valid_fragment(fragments: List[HTML], label: str, cond_parser) -> Optional[HTML]:
    for frag in fragments:
        conded = cond_parser(frag.conditions)

        if frag.label == label and conded[0]:
            return frag

    return None

def gather_numerical_tags(text: str):
    return list(reversed(list(re.finditer(r'\{\{%(\d+)\}\}', text))))

def gather_tags(text: str):
    return list(reversed(list(re.finditer(r'\{\{%(\w+)(?::(.*?))?\}\}', text))))

squote = re.compile(r"^'(.*?)'\s*?(?:,|$)")
dquote = re.compile(r'^"(.*?)"\s*?(?:,|$)')
naked = re.compile(r'^([^,]+)(?:,|$)')

from aqt.utils import showText
def match_tag_argument(text):
    if m := re.match(squote, text):
        return text[m.end():len(text)], m.group(1)
    elif m := re.match(dquote, text):
        return text[m.end():len(text)], m.group(1)
    elif m := re.match(naked, text):
        return text[m.end():len(text)], m.group(1).rstrip()

    return None

def get_tag_arguments(text: Optional[str]):
    result = []

    while text:
        next = match_tag_argument(text.lstrip())

        if not next:
            break

        text = next[0]
        result.append(next[1])

    return result

def get_special_parser(scripts, model, cardtype_name, idx, position):
    def inner_parser(keyword):
        if keyword == 'idx':
            return str(idx)

        if keyword == 'cardidx':
            return re.search(r'\d*$', cardtype_name)[0]

        elif keyword == 'scripts':
            return stringify_setting_for_template(
                scripts,
                model['name'],
                model['id'],
                cardtype_name,
                position,
            )

        return ''

    return inner_parser

def evaluate_numerical(fragment: str, arguments: List[str]):
    text = fragment
    inner_tags = gather_numerical_tags(text)

    for match in inner_tags:
        keyword = match.group(1)

        try:
            numerical = int(keyword)
            replacement = arguments[numerical - 1]

        except (ValueError, IndexError):
            replacement = ''

        text = replacement.join([
            text[0:match.start()],
            text[match.end():len(text) + 1],
        ])

    return text

def evaluate_fragment(
    fragments: List[HTML],
    entrance: str,
    cond_parser,
    special_parser,
) -> Optional[str]:
    base = find_valid_fragment(fragments, entrance, cond_parser)

    text = base.code
    inner_tags = gather_tags(text)
    iterations = 0

    while len(inner_tags) != 0 and iterations < 50:
        for match in inner_tags:
            keyword = match.group(1)
            arguments = get_tag_arguments(match.group(2))

            if keyword[0].islower():
                replacement = special_parser(keyword)

            else: # keyword[0].isupper()
                fragment = find_valid_fragment(fragments, keyword, cond_parser)
                replacement = evaluate_numerical(fragment.code, arguments) if fragment else ''

            text = replacement.join([
                text[0:match.start()],
                text[match.end():len(text) + 1],
            ])

        inner_tags = gather_tags(text)
        iterations += 1

    return text

def setup_full(model_id: int, html: HTMLSetting, scripts: ScriptSetting):
    model = mw.col.models.get(model_id)

    for idx, template in enumerate(model['tmpls']):
        # anki uses qfmt and afmt in model objects
        # I use question and answer
        cardtype_name = template['name']

        for fmt in ['qfmt', 'afmt']:
            entrance = 'Front' if fmt == 'qfmt' else 'Back'
            position = 'question' if fmt == 'qfmt' else 'answer'

            conds = get_condition_parser(cardtype_name, position)
            specials = get_special_parser(scripts, model, cardtype_name, idx + 1, position)
            result = evaluate_fragment(html.fragments, entrance, conds, specials)

            if result:
                write_model_template(template, fmt, result)

def setup_model(model_id: int, html: HTMLSetting, scripts: ScriptSetting):
    if html.enabled:
        setup_full(model_id, html, scripts)
    else:
        setup_with_only_scripts(model_id, scripts)
