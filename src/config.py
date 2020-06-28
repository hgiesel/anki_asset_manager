from os import path
from dataclasses import asdict
from typing import Union, Optional, List

from anki.cards import Card
from aqt import mw

from .config_types import (
    Setting, Script, ConcreteScript, MetaScript, ScriptStorage,
    DEFAULT_SETTING, DEFAULT_CONCRETE_SCRIPT, DEFAULT_META_SCRIPT,
)

from .lib.interface import make_setting, make_script, make_meta_script, make_script_storage
from .lib.registrar import has_interface, get_meta_scripts, has_meta_script

def deserialize_setting(model_id: int, model_setting: dict) -> Setting:
    return make_setting(
        model_setting['enabled'] if 'enabled' in model_setting else DEFAULT_SETTING.enabled,
        model_setting['insertStub'] if 'insertStub' in model_setting else DEFAULT_SETTING.insert_stub,
        model_setting['indentSize'] if 'indentSize' in model_setting else DEFAULT_SETTING.indent_size,
        add_other_metas(model_id, [s for s in [
            deserialize_script(script)
            for script
            in (model_setting['scripts'] if 'scripts' in model_setting else DEFAULT_SETTING.scripts)
        ] if s]),
    )

def add_other_metas(model_id: int, scripts: List[Script]) -> List[Script]:
    meta_scripts = get_meta_scripts(model_id)

    for ms in meta_scripts:
        try:
            found = next(filter(lambda v: isinstance(v, MetaScript) and v.tag == ms.tag and v.id == ms.id, scripts))
        except StopIteration:
            scripts.append(make_meta_script(
                ms.tag,
                ms.id,
            ))

    return scripts

def deserialize_script(script_data: dict) -> Union[ConcreteScript, MetaScript]:
    return script_data if isinstance(script_data, Script) else (
        deserialize_concrete_script(script_data)
        if 'name' in script_data
        else deserialize_meta_script(script_data)
    )

def deserialize_concrete_script(script_data: dict) -> ConcreteScript:
    return make_script(
        script_data['name'] if 'name' in script_data else DEFAULT_CONCRETE_SCRIPT.name,
        script_data['enabled'] if 'enabled' in script_data else DEFAULT_CONCRETE_SCRIPT.enabled,
        script_data['type'] if 'type' in script_data else DEFAULT_CONCRETE_SCRIPT.type,
        script_data['version'] if 'version' in script_data else DEFAULT_CONCRETE_SCRIPT.version,
        script_data['description'] if 'description' in script_data else DEFAULT_CONCRETE_SCRIPT.description,
        script_data['position'] if 'position' in script_data else DEFAULT_CONCRETE_SCRIPT.position,
        script_data['conditions'] if 'conditions' in script_data else DEFAULT_CONCRETE_SCRIPT.conditions,
        script_data['code'] if 'code' in script_data else DEFAULT_CONCRETE_SCRIPT.code,
    )

def deserialize_meta_script(script_data: dict) -> MetaScript:
    result = make_meta_script(
        script_data['tag'] if 'tag' in script_data else DEFAULT_META_SCRIPT.tag,
        script_data['id'] if 'id' in script_data else DEFAULT_META_SCRIPT.id,
        make_script_storage(**script_data['storage'] if 'storage' in script_data else DEFAULT_META_SCRIPT.storage),
    )

    return result

def serialize_setting(setting: Setting) -> dict:
    return {
        'enabled': setting.enabled,
        'insertStub': setting.insert_stub,
        'indentSize': setting.indent_size,
        'scripts': [serialize_script(script) for script in setting.scripts],
    }

def serialize_script(script: Union[ConcreteScript, MetaScript]) -> dict:
    if isinstance(script, ConcreteScript):
        return asdict(script)
    else:
        preresult = asdict(script)

        return {
            'tag': preresult['tag'],
            'id': preresult['id'],
            'storage': {
                k: v for k, v in preresult['storage'].items() if v is not None
            }
        }

def get_setting_from_notetype(notetype) -> Setting:
    return deserialize_setting(
        notetype['id'],
        (notetype['assetManager']
         if 'assetManager' in notetype and type(notetype['assetManager']) is dict
         else {}),
    )

def maybe_get_setting_from_card(card) -> Optional[Setting]:
    the_note = Card(mw.col, card.id).note()
    maybe_model = the_note.model()

    return get_setting_from_notetype(maybe_model) if maybe_model else None

def write_setting(model_id, sett: Setting):
    mw.col.models.get(model_id)['assetManager'] = serialize_setting(sett)
