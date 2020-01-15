import json
import os.path as path

from aqt import mw

from .utils import (
    safenav,
    safenav_preset,
)

from .types import (
    SMSetting,
    SMScript,
)

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
        [deserialize_script(script) for script in access_func([model_setting], ['scripts'])],
    )

def deserialize_script(script_data, access_func = safenav_script) -> SMScript:
    return script_data if type(script_data) == SMScript else SMScript(
        access_func([script_data], ['enabled']),
        access_func([script_data], ['name']),
        access_func([script_data], ['version']),
        access_func([script_data], ['description']),
        access_func([script_data], ['conditions']),
        access_func([script_data], ['code']),
    )

def serialize_setting(setting: SMSetting) -> dict:
    return {
        'modelName': setting.model_name,
        'scripts': [serialize_script(script) for script in setting.scripts],
    }

def serialize_script(script: SMScript) -> dict:
    return {
        'enabled': script.enabled,
        'name': script.name,
        'version': script.version,
        'description': script.description,
        'conditions': script.conditions,
        'code': script.code,
    }

def deserialize_setting_with_default(model_name, settings):
    found = filter(lambda v: v['modelName'] == model_name, settings)

    try:
        model_deserialized = deserialize_setting(model_name, next(found))

    except StopIteration as e:
        model_deserialized = deserialize_setting(model_name, model_default)

    return model_deserialized

def get_settings(model_name=None):
    CONFIG = mw.addonManager.getConfig(__name__)

    if model_name:
        return deserialize_setting(model_name, safenav([CONFIG], ['settings'], default=None))

    else:
        model_settings = []

        for model in mw.col.models.models.values():
            model_name = (model['name'])
            model_deserialized = deserialize_setting_with_default(model_name, safenav([CONFIG], ['settings'], default=[]))
            model_settings.append(model_deserialized)

        return model_settings

def write_settings(serializedSettings):
    from aqt.utils import showInfo
    showInfo(str(serializedSettings))

    mw.addonManager.writeConfig(__name__, {
        'settings': serializedSettings,
    })
