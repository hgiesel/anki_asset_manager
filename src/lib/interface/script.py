from typing import List

from ...config_types import (
    ScriptSetting,
    ConcreteScript,
    ScriptType,
    ScriptPosition,

    DEFAULT_CONCRETE_SCRIPT,
)

def make_setting(
    enabled: bool,
    insert_stub: bool,
    indent_size: int,
    scripts: list,
) -> ScriptSetting:
    return ScriptSetting(
        enabled,
        insert_stub,
        indent_size,
        scripts,
    )

def make_script(
    name: str = DEFAULT_CONCRETE_SCRIPT.name,
    enabled: bool = DEFAULT_CONCRETE_SCRIPT.enabled,
    type: ScriptType = DEFAULT_CONCRETE_SCRIPT.type,
    version: str = DEFAULT_CONCRETE_SCRIPT.version,
    description: str = DEFAULT_CONCRETE_SCRIPT.description,
    position: ScriptPosition = DEFAULT_CONCRETE_SCRIPT.position,
    conditions: list = DEFAULT_CONCRETE_SCRIPT.conditions,
    code: str = DEFAULT_CONCRETE_SCRIPT.code,
) -> ConcreteScript:
    return make_script_v2(
        name = name,
        enabled = enabled,
        type = type,
        version = version,
        description = description,
        position = position,
        conditions = conditions,
        code = code,
    )

def make_script_v2(
    *,
    name: str = DEFAULT_CONCRETE_SCRIPT.name,
    enabled: bool = DEFAULT_CONCRETE_SCRIPT.enabled,
    type: ScriptType = DEFAULT_CONCRETE_SCRIPT.type,
    label: str = DEFAULT_CONCRETE_SCRIPT.label,
    version: str = DEFAULT_CONCRETE_SCRIPT.version,
    description: str = DEFAULT_CONCRETE_SCRIPT.description,
    position: ScriptPosition = DEFAULT_CONCRETE_SCRIPT.position,
    conditions: list = DEFAULT_CONCRETE_SCRIPT.conditions,
    code: str = DEFAULT_CONCRETE_SCRIPT.code,
) -> ConcreteScript:
    possible_types = ['js', 'esm', 'css']
    possible_positions = ['external', 'head', 'body', 'into_template']

    return ConcreteScript(
        name if name is not None else DEFAULT_CONCRETE_SCRIPT.name,
        enabled if enabled is not None else DEFAULT_CONCRETE_SCRIPT.enabled,
        type if type in possible_types else DEFAULT_CONCRETE_SCRIPT.type,
        label if name is not None else DEFAULT_CONCRETE_SCRIPT.label,
        version if version is not None else DEFAULT_CONCRETE_SCRIPT.version,
        description if description is not None else DEFAULT_CONCRETE_SCRIPT.description,
        position if position in possible_positions else DEFAULT_CONCRETE_SCRIPT.position,
        conditions if conditions is not None else DEFAULT_CONCRETE_SCRIPT.conditions,
        code if code is not None else DEFAULT_CONCRETE_SCRIPT.code,
    )
