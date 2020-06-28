import os
import io
import re
import base64

from json import dumps
from string import Template

from anki import media
from aqt import mw

from ..config import get_setting_from_notetype

from .stringify import stringify_setting

def setup_model(modelId: int):
    needs_saving = False
    model = mw.col.models.get(modelId)

    for template in model['tmpls']:
        setting = get_setting_from_notetype(model)

        for fmt in ['qfmt', 'afmt']:
            did_insert = update_model_template(
                template,
                fmt,
                stringify_setting(
                    setting,
                    model['name'],
                    template['name'],
                    fmt,
                    'into_template',
                ),
            )

            needs_saving = needs_saving or did_insert

    # notify anki that models changed (for synchronization e.g.)
    if needs_saving:
        mw.col.models.save(model, True)

def get_template_slice(t):
    try:
        startpos_regex = re.compile(r'\n?\n? *?<div.*?id="anki\-am".*?>', re.MULTILINE)
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
