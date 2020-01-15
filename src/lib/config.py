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
        access_func([model_setting], ['meta'], default={}),
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
    result = {
        'modelName': setting.model_name,
        'scripts': [serialize_script(script) for script in setting.scripts],
    }

    if setting.meta and len(setting.meta.keys()) > 0:
        result['meta'] = setting.meta

    return result

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

def sr_to_sm_setting():
    pass

def anki_persistence_to_sm_setting():
    pass

def get_settings(sr=None):
    config = mw.addonManager.getConfig(__name__)
    sr_config = mw.addonManager.getConfig(sr) if sr else None

    from aqt.utils import showInfo
    # showInfo(str(model))

    def get_setting(model_name):
        return filter(lambda v: v['modelName'] == model_name, safenav([config], ['settings'], default=None))

    model_settings = []

    for model in mw.col.models.models.values():
        model_name = model['name']
        model_deserialized = deserialize_setting_with_default(model_name, get_setting(model_name))

        for model_sr in safenav([sr_config], ['settings'], default=[]):
            if model_sr['enabled'] and model_sr['modelName'] == model_name:

                if not safenav([model_deserialized.meta], ['set_randomizer'], default=False):
                    model_deserialized.meta['set_randomizer'] = True

                if not safenav([model_deserialized.meta], ['anki_persistence'], default=False):
                    model_deserialized.meta['anki_persistence_from_sr'] = True

        model_settings.append(model_deserialized)

    return model_settings

def write_settings(serializedSettings):
    mw.addonManager.writeConfig(__name__, {
        'settings': serializedSettings,
    })
