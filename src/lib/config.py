import json
import os.path as path

from dataclasses import asdict
from typing import Union, Optional, List

from aqt import mw

from .utils import safenav, safenav_preset

from .types import SMSetting, SMScript, SMConcrScript, SMMetaScript, SMScriptStorage
from .interface import make_setting, make_script, make_meta_script, make_script_storage
from .registrar import has_interface, get_meta_scripts, meta_script_is_registered

# initialize default type
SCRIPTNAME = path.dirname(path.realpath(__file__))

with open(path.join(SCRIPTNAME, '../../config.json'), encoding='utf-8') as config:
    config_default = json.load(config)

    SETTINGS_DEFAULT = config_default['settings'][0]
    model_default = SETTINGS_DEFAULT

    safenav_setting = safenav_preset(model_default)
    safenav_concr_script = safenav_preset(model_default['scripts'][0])
    safenav_meta_script = safenav_preset(model_default['scripts'][1])

def deserialize_setting(model_name, model_setting, access_func = safenav_setting) -> SMSetting:
    return model_setting if isinstance(model_setting, SMSetting) else make_setting(
        model_name,
        access_func([model_setting], ['enabled']),
        access_func([model_setting], ['insertStub']),
        access_func([model_setting], ['indentSize']),
        add_other_metas(model_name, [s for s in [deserialize_script(model_name, script)
         for script
         in access_func([model_setting], ['scripts'])] if s]),
    )

def add_other_metas(model_name, scripts: List[SMScript]) -> List[SMScript]:
    meta_scripts = get_meta_scripts(model_name)

    for ms in meta_scripts:
        try:
            found = next(filter(lambda v: isinstance(v, SMMetaScript) and v.tag == ms.tag and v.id == ms.id, scripts))
        except StopIteration:
            scripts.append(make_meta_script(
                ms.tag,
                ms.id,
            ))

    return scripts

def deserialize_script(model_name, script_data) -> Union[SMConcrScript, SMMetaScript]:
    return script_data if isinstance(script_data, SMScript) else (
        deserialize_concr_script(script_data)
        if 'name' in script_data
        else deserialize_meta_script(model_name, script_data)
    )

def deserialize_concr_script(script_data, access_func = safenav_concr_script) -> SMConcrScript:
    result = script_data if isinstance(script_data, SMConcrScript) else make_script(
        access_func([script_data], ['enabled']),
        access_func([script_data], ['name']),
        access_func([script_data], ['version']),
        access_func([script_data], ['description']),
        access_func([script_data], ['conditions']),
        access_func([script_data], ['code']),
    )

    return result

def deserialize_meta_script(model_name, script_data, access_func = safenav_meta_script) -> Optional[SMMetaScript]:
    result = script_data if isinstance(script_data, SMMetaScript) else make_meta_script(
        access_func([script_data], ['tag']),
        access_func([script_data], ['id']),
        make_script_storage(**access_func([script_data], ['storage'], default = {})),
    )

    return result if has_interface(result.tag) and meta_script_is_registered(
        model_name,
        result.tag,
        result.id,
    ) else None

def serialize_setting(setting: SMSetting) -> dict:
    return {
        'modelName': setting.model_name,
        'enabled': setting.enabled,
        'insertStub': setting.insert_stub,
        'indentSize': setting.indent_size,
        'scripts': [serialize_script(script) for script in setting.scripts],
    }

def serialize_script(script: Union[SMConcrScript, SMMetaScript]) -> dict:
    if isinstance(script, SMConcrScript):
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

def deserialize_setting_with_default(model_name, settings):
    found = filter(lambda v: v['modelName'] == model_name, settings)

    try:
        model_deserialized = deserialize_setting(model_name, next(found))

    except StopIteration:
        model_deserialized = deserialize_setting(model_name, model_default)

    return model_deserialized

def get_settings():
    config = mw.addonManager.getConfig(__name__)

    def get_setting(model_name):
        return filter(lambda v: v['modelName'] == model_name, safenav([config], ['settings'], default=None))

    model_settings = []

    for model in mw.col.models.models.values():
        model_name = model['name']
        model_deserialized = deserialize_setting_with_default(model_name, get_setting(model_name))

        model_settings.append(model_deserialized)

    return model_settings

def write_settings(serializedSettings):
    mw.addonManager.writeConfig(__name__, {
        'settings': serializedSettings,
    })
