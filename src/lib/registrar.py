from typing import Optional, List, Tuple, Callable, Union

from ..config_types import (
    Interface,
    Script,
    MetaScript,
    ConcreteScript,

    ScriptStorage,
    ScriptKeys,
    ScriptText,
    ScriptInsertion,

    AnkiModel,
    AnkiTmpl,
    LabelText,
    Falsifiable,

    LabelReducer,
    DEFAULT_REDUCER,
)

from .interface import make_interface, make_script_v2, make_reducer


############## META INTERFACES

_meta_interfaces: List[Interface] = []

def make_and_register_interface(
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
    register_interface(make_interface(
        tag = tag,
        getter = getter,
        setter = setter,
        generator = generator,
        label = label,
        reset = reset,
        deletable = deletable,
        autodelete = autodelete,
        readonly = readonly,
        store = store,
    ))

def register_interface(iface: Interface) -> None:
    _meta_interfaces.append(iface)

loose_script = make_script_v2(
    name = '',
    enabled = False,
    type = 'js',
    label = '',
    version = '',
    description = '',
    position = 'into_template',
    conditions = [],
    code = '',
)

all_attributes = ['name', 'enabled', 'type', 'label', 'version', 'description', 'position', 'conditions', 'code']

def make_loose_interface(tag: str) -> Interface:
    return make_interface(
        tag = tag,
        getter = lambda id, storage: make_script_v2(
            name = storage.name if storage.name is not None else loose_script.name,
            enabled = storage.enabled if storage.enabled is not None else loose_script.enabled,
            type = storage.type if storage.type is not None else loose_script.type,
            label = storage.label if storage.label is not None else loose_script.label,
            version = storage.version if storage.version is not None else loose_script.version,
            description = storage.description if storage.description is not None else loose_script.description,
            position = storage.position if storage.position is not None else loose_script.position,
            conditions = storage.conditions if storage.conditions is not None else loose_script.conditions,
            code = storage.code if storage.code is not None else loose_script.code,
        ),
        setter = lambda id, script: False,
        generator = lambda id, storage, model, tmpl, pos: '',
        reset = False,
        deletable = lambda id, storage: True,
        autodelete = False,
        readonly = all_attributes,
        store = all_attributes,
    )

def get_interface(tag: str) -> Interface:
    try:
        return next(filter(lambda v: v.tag == tag, _meta_interfaces))
    except StopIteration:
        return make_loose_interface(tag)

def has_interface(tag: str) -> bool:
    try:
        next(filter(lambda v: v.tag == tag, _meta_interfaces))
        return True
    except StopIteration:
        return False

############## META SCRIPTS

_meta_scripts: List[Tuple[str, MetaScript]] = []

class InterfaceIsNotRegistered(Exception):
    pass

# needs to be cast to int
ModelId = Union[int, str]

def register_meta_script(model_id: ModelId, meta_script: MetaScript) -> None:
    mid = int(model_id)

    if has_interface(meta_script.tag):
        _meta_scripts.append((mid, meta_script,))
    else:
        raise InterfaceIsNotRegistered(
            'You tried to register a meta script for a non existing interface. '
            'Make sure to register the interface first.'
        )

def deregister_meta_script(model_id: ModelId, meta_script: MetaScript) -> bool:
    mid = int(model_id)

    if has_interface(meta_script.tag):
        try:
            found = next(filter(lambda v: (
                v[1][0] == mid
                and v[1][1].tag == meta_script.tag
                and v[1][1].id == meta_script.id
            ), enumerate(_meta_scripts)))

            _meta_scripts.pop(found[0])
            return True

        except StopIteration:
            return False

    else:
        raise InterfaceIsNotRegistered(
            'You tried to deregister a meta script for a non existing interface. '
            'Make sure to register the interface first.'
        )

def get_meta_scripts(model_id: Optional[ModelId] = None) -> List[MetaScript]:
    mid = int(model_id) if model_id else None

    return [
        ms[1] for ms in _meta_scripts if (
            ms[0] == mid or mid is None
        )
    ]

def get_meta_script(model_id: ModelId, tag: str, id: str) -> Optional[MetaScript]:
    mid = int(model_id)

    try:
        return next(filter(
            lambda v: (
                v[0] == mid and
                v[1].tag == tag and
                v[1].id == id
            ),
            _meta_scripts,
        ))

    except StopIteration:
        return None

def has_meta_script(model_id: ModelId, tag: str, id: str) -> bool:
    mid = int(model_id)

    try:
        next(filter(
            lambda v: (
                v[0] == mid and
                v[1].tag == tag and
                v[1].id == id
            ),
            _meta_scripts,
        ))
        return True

    except StopIteration:
        return False

############## LABEL REDUCER

_label_reducers: List[LabelReducer] = []

def make_and_register_reducer(
    label: str,
    reducer: Callable[[List[str]], str],
) -> LabelReducer:
    register_reducer(make_reducer(
        label = label,
        reducer = reducer,
    ))

def register_reducer(redux: LabelReducer) -> None:
    _label_reducers.append(redux)

def get_reducer(label: str) -> LabelReducer:
    try:
        return next(filter(lambda v: v.label == label, _label_reducers))
    except StopIteration:
        return DEFAULT_REDUCER

def has_reducer(label: str) -> bool:
    try:
        next(filter(lambda v: v.label == label, _label_reducers))
        return True
    except StopIteration:
        return False
