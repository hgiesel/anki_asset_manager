from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

from .types import (
    SMInterface, SMSetting, SMConcrScript, SMMetaScript, SMScriptBool, SMScriptStorage,
    anki_model, anki_tmpl, anki_fmt, script_text, label_text,
)

def make_setting(
    model_name: str,
    enabled: bool,
    indent_size: int,
    scripts: list,
) -> SMSetting:
    return SMSetting(
        model_name,
        enabled,
        indent_size,
        scripts,
    )

def make_script(
    enabled: bool,
    name: str,
    version: str,
    description: str,
    conditions: list,
    code: str,
) -> SMConcrScript:
    return SMConcrScript(
        enabled,
        name,
        version,
        description,
        conditions,
        code,
    )

def make_meta_script(
    tag: str,
    id: str,
    storage: Optional[SMScriptStorage] = None
) -> SMMetaScript:
    return SMMetaScript(
        tag,
        id,
        storage if storage is not None else make_script_storage()
    )

def make_script_bool(
    enabled: Optional[bool] = None,
    name: Optional[bool] = None,
    version: Optional[bool] = None,
    description: Optional[bool] = None,
    conditions: Optional[bool] = None,
    code: Optional[bool] = None,
) -> SMScriptBool:
    return SMScriptBool(
        enabled if enabled is not None else False,
        name if name is not None else False,
        version if version is not None else False,
        description if description is not None else False,
        conditions if conditions is not None else False,
        code if code is not None else False,
    )

def make_script_storage(
    enabled: Optional[bool] = None,
    name: Optional[str] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
    conditions: Optional[list] = None,
    code: Optional[str] = None,
) -> SMScriptStorage:
    return SMScriptStorage(
        enabled,
        name,
        version,
        description,
        conditions,
        code,
    )

ScriptKeys = Literal['enabled', 'name', 'version', 'description', 'conditions', 'code']

def __list_to_sm_script_bool(vals: List[ScriptKeys]) -> SMScriptBool:
    return replace(
        make_script_bool(),
        **dict([(key, True) for key in vals])
    )

def make_interface(
    tag: str,
    getter: Callable[[str, SMScriptStorage], SMConcrScript],
    setter: Callable[[str, SMConcrScript], Union[bool, SMConcrScript]],
    generator: Optional[Callable[[str, SMScriptStorage, anki_model, anki_tmpl, anki_fmt], Union[script_text, Literal[False]]]] = None,
    label: Optional[Union[Literal[False], Callable[[str, SMScriptStorage], label_text]]] = None,
    reset: Optional[Union[Literal[False], Callable[[str, SMScriptStorage], SMConcrScript]]] = None,
    deletable: Optional[Union[Literal[False], Callable[[str, SMScriptStorage], bool]]] = None,
    readonly: Optional[Union[List[ScriptKeys], SMScriptStorage]] = None,
    store: Optional[Union[List[ScriptKeys], SMScriptStorage]] = None,
) -> SMInterface:
    return SMInterface(
        tag,
        getter,
        setter,
        generator if generator is not None else lambda id, storage, _model, _tmpl, _fmt: getter(id, storage).code,
        label if label is not None else lambda id, _storage: f"{tag}: {id}",
        reset if reset is not None else lambda id, _storage: getter(id, make_script_storage()),
        deletable if deletable is not None else lambda _id, _storage: False,
        readonly if isinstance(readonly, SMScriptStorage) else (
            __list_to_sm_script_bool(readonly) if readonly is not None else make_script_bool()
        ),
        store if isinstance(store, SMScriptStorage) else (
            __list_to_sm_script_bool(store) if store is not None else make_script_bool()
        ),
    )
