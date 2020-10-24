from typing import Optional, Callable, Union, List
from dataclasses import replace

from ...config_types import (
    Falsifiable,
    ScriptType,
    ScriptStorage,
    ScriptBool,
    ScriptKeys,

    AnkiModel,
    AnkiTmpl,
    ScriptInsertion,
    ScriptText,
    LabelText,

    MetaScript,
    ConcreteScript,
    Interface,
)


def make_script_storage(
    name: Optional[str] = None,
    enabled: Optional[bool] = None,
    type: Optional[ScriptType] = None,
    label: Optional[str] = None,
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
        label,
        version,
        description,
        position,
        conditions,
        code,
    )

def make_script_bool(
    name: Optional[bool] = None,
    enabled: Optional[bool] = None,
    type: Optional[bool] = None,
    label: Optional[bool] = None,
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
        label if label is not None else False,
        version if version is not None else False,
        description if description is not None else False,
        position if position is not None else False,
        conditions if conditions is not None else False,
        code if code is not None else False,
    )

def __list_to_script_bool(
    vals: List[ScriptKeys],
) -> ScriptBool:
    return replace(
        make_script_bool(),
        **dict([(key, True) for key in vals])
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

def make_interface(
    tag: str,
    *,
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
