from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

from ..config_types import (
    Interface, Setting, ConcreteScript, MetaScript,
    ScriptBool, ScriptStorage, ScriptType,
    AnkiModel, AnkiTmpl, AnkiFmt, ScriptText, LabelText, Falsifiable,
)

def make_setting(
    enabled: bool,
    insert_stub: bool,
    indent_size: int,
    scripts: list,
) -> Setting:
    return Setting(
        enabled,
        insert_stub,
        indent_size,
        scripts,
    )

def make_script(
    enabled: bool,
    type: ScriptType,
    name: str,
    version: str,
    description: str,
    conditions: list,
    code: str,
) -> ConcreteScript:
    return ConcreteScript(
        enabled,
        type,
        name,
        version,
        description,
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
    enabled: Optional[bool] = None,
    type: Optional[bool] = None,
    name: Optional[bool] = None,
    version: Optional[bool] = None,
    description: Optional[bool] = None,
    conditions: Optional[bool] = None,
    code: Optional[bool] = None,
) -> ScriptBool:
    return ScriptBool(
        enabled if enabled is not None else False,
        type if type is not None else False,
        name if name is not None else False,
        version if version is not None else False,
        description if description is not None else False,
        conditions if conditions is not None else False,
        code if code is not None else False,
    )

def make_script_storage(
    enabled: Optional[bool] = None,
    type: Optional[ScriptType] = None,
    name: Optional[str] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
    conditions: Optional[list] = None,
    code: Optional[str] = None,
) -> ScriptStorage:
    return ScriptStorage(
        enabled,
        type,
        name,
        version,
        description,
        conditions,
        code,
    )

ScriptKeys = Literal['enabled', 'type', 'name', 'version', 'description', 'conditions', 'code']

def __list_to_script_bool(vals: List[ScriptKeys]) -> ScriptBool:
    return replace(
        make_script_bool(),
        **dict([(key, True) for key in vals])
    )

def make_interface(
    tag: str,
    getter: Callable[[str, ScriptStorage], ConcreteScript],
    setter: Callable[[str, ConcreteScript], Union[bool, ConcreteScript]],
    generator: Optional[Callable[[str, ScriptStorage, AnkiModel, AnkiTmpl, AnkiFmt], Falsifiable(ScriptText)]] = None,
    label: Optional[Falsifiable(Callable[[str, ScriptStorage], LabelText])] = None,
    reset: Optional[Falsifiable(Callable[[str, ScriptStorage], ConcreteScript])] = None,
    deletable: Optional[Falsifiable(Callable[[str, ScriptStorage], bool])] = None,
    readonly: Optional[Union[List[ScriptKeys], ScriptStorage]] = None,
    store: Optional[Union[List[ScriptKeys], ScriptStorage]] = None,
) -> Interface:
    return Interface(
        tag,
        getter,
        setter,
        generator if generator is not None else lambda id, storage, _model, _tmpl, _fmt: getter(id, storage).code,
        label if label is not None else lambda id, _storage: f"{tag}: {id}",
        reset if reset is not None else lambda id, _storage: getter(id, make_script_storage()),
        deletable if deletable is not None else lambda _id, _storage: False,
        readonly if isinstance(readonly, ScriptStorage) else (
            __list_to_script_bool(readonly) if readonly is not None else make_script_bool()
        ),
        store if isinstance(store, ScriptStorage) else (
            __list_to_script_bool(store) if store is not None else make_script_bool()
        ),
    )
