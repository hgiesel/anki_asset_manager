from os import path
from dataclasses import asdict
from typing import Union, Optional, List

from anki.cards import Card
from aqt import mw

from .config_types import (
    ScriptSetting, Script, ConcreteScript, MetaScript, ScriptStorage,
    DEFAULT_SETTING, DEFAULT_CONCRETE_SCRIPT, DEFAULT_META_SCRIPT,

    HTMLSetting, HTML, ConcreteHTML,
    DEFAULT_HTML_SETTING, DEFAULT_CONCRETE_HTML,
)

from .lib.interface import (
    make_setting, make_script, make_meta_script, make_script_storage,
    make_html_setting, make_fragment,
)

from .lib.registrar import get_interface, has_interface, get_meta_scripts, has_meta_script

######################## scripts

scriptsKeyword = 'assetManager'

def deserialize_setting(model_id: int, model_setting: dict) -> ScriptSetting:
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

def should_autodelete(script: Script) -> bool:
    if isinstance(script, ConcreteScript):
        return False

    interface = get_interface(script.tag)

    if isinstance(interface.autodelete, bool):
        return interface.autodelete

    return interface.autodelete(script.id, script.storage)

def add_other_metas(model_id: int, scripts: List[Script]) -> List[Script]:
    meta_scripts = get_meta_scripts(model_id)

    for ms in meta_scripts:
        try:
            found = next(filter(lambda script: isinstance(script, MetaScript) and script.tag == ms.tag and script.id == ms.id, scripts))
        except StopIteration:
            # newly inserted meta scripts, which were not written to config before
            scripts.append(make_meta_script(
                ms.tag,
                ms.id,
            ))

    return list(filter(lambda script: not should_autodelete(script), scripts))

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
        script_data['label'] if 'label' in script_data else DEFAULT_CONCRETE_SCRIPT.label,
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
        make_script_storage(
            **script_data['storage']
            if 'storage' in script_data
            else DEFAULT_META_SCRIPT.storage
        ),
    )

    return result

def serialize_setting(setting: ScriptSetting) -> dict:
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

def get_setting_from_notetype(notetype) -> ScriptSetting:
    return deserialize_setting(
        notetype['id'],
        (notetype[scriptsKeyword]
         if scriptsKeyword in notetype and type(notetype[scriptsKeyword]) is dict
         else {}),
    )

def maybe_get_setting_from_card(card) -> Optional[ScriptSetting]:
    the_note = Card(mw.col, card.id).note()
    maybe_model = the_note.model()

    return get_setting_from_notetype(maybe_model) if maybe_model else None

######################## html

htmlKeyword = 'assetManagerHtml'

def deserialize_html_setting(model_id: int, model_setting: dict) -> ScriptSetting:
    return make_html_setting(
        model_setting['enabled'] if 'enabled' in model_setting else DEFAULT_HTML_SETTING.enabled,
        [
            deserialize_html(fragment)
            for fragment
            in (model_setting['fragments'] if 'fragments' in model_setting else DEFAULT_HTML_SETTING.fragments)
        ],
    )

def deserialize_html(script_data: dict) -> ConcreteHTML:
    return script_data if isinstance(script_data, HTML) else make_fragment(
        script_data['name'] if 'name' in script_data else DEFAULT_CONCRETE_HTML.name,
        script_data['enabled'] if 'enabled' in script_data else DEFAULT_CONCRETE_HTML.enabled,
        script_data['label'] if 'label' in script_data else DEFAULT_CONCRETE_HTML.label,
        script_data['version'] if 'version' in script_data else DEFAULT_CONCRETE_HTML.version,
        script_data['description'] if 'description' in script_data else DEFAULT_CONCRETE_HTML.description,
        script_data['conditions'] if 'conditions' in script_data else DEFAULT_CONCRETE_HTML.conditions,
        script_data['code'] if 'code' in script_data else DEFAULT_CONCRETE_HTML.code,
    )

def serialize_html_setting(setting: HTMLSetting) -> dict:
    return {
        'enabled': setting.enabled,
        'fragments': [serialize_html(script) for script in setting.fragments],
    }

def serialize_html(fragment: Union[ConcreteHTML]) -> dict:
    return asdict(fragment)

def get_html_setting_from_notetype(notetype) -> HTMLSetting:
    return deserialize_html_setting(
        notetype['id'],
        (notetype[htmlKeyword]
         if htmlKeyword in notetype and type(notetype[htmlKeyword]) is dict
         else {}),
    )

######################## together

def write_setting(model_id: int, html: HTMLSetting, scripts: ScriptSetting):
    model = mw.col.models.get(model_id)

    model[htmlKeyword] = serialize_html_setting(html)
    model[scriptsKeyword] = serialize_setting(scripts)
