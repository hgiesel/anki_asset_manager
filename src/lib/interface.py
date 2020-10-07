from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

from ..config_types import (
    Interface, ScriptSetting, ConcreteScript, MetaScript,
    ScriptBool, ScriptStorage, ScriptPosition, ScriptType, ScriptKeys,
    AnkiModel, AnkiTmpl, ScriptInsertion, ScriptText, LabelText, Falsifiable,
    DEFAULT_CONCRETE_SCRIPT,

    HTMLSetting, ConcreteHTML, HTMLBool,
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
    name: str,
    enabled: bool,
    type: ScriptType,
    version: str,
    description: str,
    position: ScriptPosition,
    conditions: list,
    code: str,
) -> ConcreteScript:
    possible_types = ['js', 'css']
    possible_positions = ['external', 'head', 'body', 'into_template']

    return ConcreteScript(
        name,
        enabled,
        type if type in possible_types else DEFAULT_CONCRETE_SCRIPT.type,
        version,
        description,
        position if position in possible_positions else DEFAULT_CONCRETE_SCRIPT.position,
        conditions,
        code,
    )

def make_meta_script(
    tag: str,
    id: str,
    storage: Optional[ScriptStorage] = None
) -> MetaScript:
    return MetaScript(
        tag,
        id,
        storage if storage is not None else make_script_storage()
    )

def make_script_bool(
    name: Optional[bool] = None,
    enabled: Optional[bool] = None,
    type: Optional[bool] = None,
    version: Optional[bool] = None,
    description: Optional[bool] = None,
    position: Optional[bool] = None,
    conditions: Optional[bool] = None,
    code: Optional[bool] = None,
) -> ScriptBool:
    return ScriptBool(
        name if name is not None else False,
        enabled if enabled is not None else False,
        type if type is not None else False,
        version if version is not None else False,
        description if description is not None else False,
        position if position is not None else False,
        conditions if conditions is not None else False,
        code if code is not None else False,
    )

def make_script_storage(
    name: Optional[str] = None,
    enabled: Optional[bool] = None,
    type: Optional[ScriptType] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
    position: Optional[list] = None,
    conditions: Optional[list] = None,
    code: Optional[str] = None,
) -> ScriptStorage:
    return ScriptStorage(
        name,
        enabled,
        type,
        version,
        description,
        position,
        conditions,
        code,
    )

def __list_to_script_bool(vals: List[ScriptKeys]) -> ScriptBool:
    return replace(
        make_script_bool(),
        **dict([(key, True) for key in vals])
    )

def make_interface(
    tag: str,
    getter: Callable[[str, ScriptStorage], ConcreteScript],
    setter: Callable[[str, ConcreteScript], Union[bool, ConcreteScript]],
    generator: Optional[Callable[[str, ScriptStorage, AnkiModel, AnkiTmpl, ScriptInsertion], Falsifiable(ScriptText)]] = None,
    label: Optional[Falsifiable(Callable[[str, ScriptStorage], LabelText])] = None,
    reset: Optional[Falsifiable(Callable[[str, ScriptStorage], ConcreteScript])] = None,
    deletable: Optional[Falsifiable(Callable[[str, ScriptStorage], bool])] = None,
    autodelete: Optional[Falsifiable(Callable[[str, ScriptStorage], bool])] = None,
    readonly: Optional[Union[List[ScriptKeys], ScriptStorage]] = None,
    store: Optional[Union[List[ScriptKeys], ScriptStorage]] = None,
) -> Interface:
    return Interface(
        tag,
        getter,
        setter,
        generator if generator is not None else lambda id, storage, _model, _tmpl, _pos: getter(id, storage).code,
        label if label is not None else lambda id, _storage: f"{tag}: {id}",
        reset if reset is not None else lambda id, _storage: getter(id, make_script_storage()),
        deletable if deletable is not None else lambda _id, _storage: False,
        autodelete if autodelete is not None else lambda _id, _storage: False,
        readonly if isinstance(readonly, ScriptStorage) else (
            __list_to_script_bool(readonly) if readonly is not None else make_script_bool()
        ),
        store if isinstance(store, ScriptStorage) else (
            __list_to_script_bool(store) if store is not None else make_script_bool()
        ),
    )

######################## html

def make_html_setting(
    enabled: bool,
    fragments: list,
) -> HTMLSetting:
    return HTMLSetting(
        enabled,
        fragments,
    )

def make_html_bool(
    name: Optional[bool] = None,
    enabled: Optional[bool] = None,
    label: Optional[bool] = None,
    version: Optional[bool] = None,
    description: Optional[bool] = None,
    conditions: Optional[bool] = None,
    code: Optional[bool] = None,
) -> HTMLBool:
    return HTMLBool(
        name if name is not None else False,
        enabled if enabled is not None else False,
        label if label is not None else False,
        version if version is not None else False,
        description if description is not None else False,
        conditions if conditions is not None else False,
        code if code is not None else False,
    )

def __list_to_html_bool(vals: List[ScriptKeys]) -> HTMLBool:
    return replace(
        make_html_bool(),
        **dict([(key, True) for key in vals])
    )

def make_fragment(
    name: str,
    enabled: bool,
    label: str,
    version: str,
    description: str,
    conditions: list,
    code: str,
) -> ConcreteHTML:
    return ConcreteHTML(
        name,
        enabled,
        label,
        version,
        description,
        conditions,
        code,
    )
