from ..config_types import ScriptSetting, Fmt
from ..utils import version

from .stringify import stringify_setting, stringify_script_data, prevent_reinclusion, encapsulate_scripts

def stringify_setting_for_template(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
    cardtype_name: str,
    fmt: Fmt,
) -> str:
    stringified_scripts = stringify_setting(
        setting,
        model_name,
        model_id,
        cardtype_name,
        fmt,
    )

    if not setting.insert_stub and fmt == 'question':
        stringified_scripts.insert(0, stringify_script_data(prevent_reinclusion, setting.indent_size, True))

    code_string = encapsulate_scripts(
        stringified_scripts,
        version,
        setting.indent_size,
    ) if setting.enabled else ''

    return code_string

def stringify_setting_for_head(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
    cardtype_name: str,
) -> str:
    return '\n'.join(stringify_setting(
        setting,
        model_name,
        model_id,
        cardtype_name,
        'head',
    ))

def stringify_setting_for_body(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
    cardtype_name: str,
) -> str:
    return '\n'.join(stringify_setting(
        setting,
        model_name,
        model_id,
        cardtype_name,
        'body',
    ))

# this is never called, this is how it should look though
def stringify_setting_for_external(
    setting: ScriptSetting,
    model_name: str,
    model_id: int,
) -> str:
    return stringify_setting(setting, model_name, model_id, None, 'external')
