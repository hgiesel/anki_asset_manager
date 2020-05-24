from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

from .config_types import (
    AMInterface, AMSetting, AMConcrScript, AMMetaScript, AMScriptBool, AMScriptStorage,
    AnkiModel, AnkiTmpl, AnkiFmt, ScriptText, LabelText, Falsifiable,
)

def make_setting(
    model_name: str,
    enabled: bool,
    insert_stub: bool,
    indent_size: int,
    scripts: list,
) -> AMSetting:
    return AMSetting(
        model_name,
        enabled,
        insert_stub,
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
) -> AMConcrScript:
    return AMConcrScript(
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
    storage: Optional[AMScriptStorage] = None
) -> AMMetaScript:
    return AMMetaScript(
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
) -> AMScriptBool:
    return AMScriptBool(
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
) -> AMScriptStorage:
    return AMScriptStorage(
        enabled,
        name,
        version,
        description,
        conditions,
        code,
    )

ScriptKeys = Literal['enabled', 'name', 'version', 'description', 'conditions', 'code']

def __list_to_am_script_bool(vals: List[ScriptKeys]) -> AMScriptBool:
    return replace(
        make_script_bool(),
        **dict([(key, True) for key in vals])
    )

def make_interface(
    tag: str,
    getter: Callable[[str, AMScriptStorage], AMConcrScript],
    setter: Callable[[str, AMConcrScript], Union[bool, AMConcrScript]],
    generator: Optional[Callable[[str, AMScriptStorage, AnkiModel, AnkiTmpl, AnkiFmt], Falsifiable(ScriptText)]] = None,
    label: Optional[Falsifiable(Callable[[str, AMScriptStorage], LabelText])] = None,
    reset: Optional[Falsifiable(Callable[[str, AMScriptStorage], AMConcrScript])] = None,
    deletable: Optional[Falsifiable(Callable[[str, AMScriptStorage], bool])] = None,
    readonly: Optional[Union[List[ScriptKeys], AMScriptStorage]] = None,
    store: Optional[Union[List[ScriptKeys], AMScriptStorage]] = None,
) -> AMInterface:
    return AMInterface(
        tag,
        getter,
        setter,
        generator if generator is not None else lambda id, storage, _model, _tmpl, _fmt: getter(id, storage).code,
        label if label is not None else lambda id, _storage: f"{tag}: {id}",
        reset if reset is not None else lambda id, _storage: getter(id, make_script_storage()),
        deletable if deletable is not None else lambda _id, _storage: False,
        readonly if isinstance(readonly, AMScriptStorage) else (
            __list_to_am_script_bool(readonly) if readonly is not None else make_script_bool()
        ),
        store if isinstance(store, AMScriptStorage) else (
            __list_to_am_script_bool(store) if store is not None else make_script_bool()
        ),
    )
