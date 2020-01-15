import json
import attr
import os.path as path

from aqt import mw

from .utils import (
    safenav,
    safenav_preset,
)

from .types import (
    SMSetting,
    SMScript,
    SMMetaScript,
)

from .interface import has_interface

# initialize default type
SCRIPTNAME = path.dirname(path.realpath(__file__))

with open(path.join(SCRIPTNAME, '../../config.json'), encoding='utf-8') as config:
    config_default = json.load(config)

    SETTINGS_DEFAULT = config_default['settings'][0]
    model_default = SETTINGS_DEFAULT

    safenav_setting = safenav_preset(model_default)
    safenav_script = safenav_preset(model_default['scripts'][0])

def deserialize_setting(model_name, model_setting, access_func = safenav_setting) -> SMSetting:
    return model_setting if type(model_setting) == SMSetting else SMSetting(
        model_name,
        [deserialize_script(script)
         for script
         in access_func([model_setting], ['scripts'])],
    )

def deserialize_script(script_data) -> SMScript or SMScript:
    return script_data if type(script_data) in [SMScript, SMMetaScript] else (
        deserialize_concr_script(script_data)
        if 'name' in script_data
        else deserialize_meta_script(script_data)
    )

def deserialize_concr_script(script_data, access_func = safenav_script) -> SMScript:
    return script_data if type(script_data) == SMScript else SMScript(
        access_func([script_data], ['enabled']),
        access_func([script_data], ['name']),
        access_func([script_data], ['version']),
        access_func([script_data], ['description']),
        access_func([script_data], ['conditions']),
        access_func([script_data], ['code']),
    )

def deserialize_meta_script(script_data, access_func = safenav_script) -> SMMetaScript or None:
    result = script_data if type(script_data) == SMMetaScript else SMMetaScript(
        access_func([script_data], ['tag']),
        access_func([script_data], ['id']),
        SMScriptStorage(**access_func([script_data], ['storage'])),
    )

    return result if has_interface(result.tag) else None

def serialize_setting(setting: SMSetting) -> dict:
    return {
        'modelName': setting.model_name,
        'scripts': [serialize_script(script) for script in setting.scripts],
    }

def serialize_script(script: SMScript or SMMetaScript) -> dict:
    return attr.asdict(script)

def deserialize_setting_with_default(model_name, settings):
    found = filter(lambda v: v['modelName'] == model_name, settings)

    try:
        model_deserialized = deserialize_setting(model_name, next(found))

    except StopIteration as e:
        model_deserialized = deserialize_setting(model_name, model_default)

    return model_deserialized

def get_settings():
    config = mw.addonManager.getConfig(__name__)
    # sr_config = mw.addonManager.getConfig(sr) if sr else None

    from aqt.utils import showInfo
    # showInfo(str(model))

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
