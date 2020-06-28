from typing import Optional, List, Tuple, Callable, Union

from ..config_types import (
    Interface, MetaScript, ConcreteScript,
    ScriptStorage, ScriptKeys, ScriptText,
    Falsifiable, AnkiModel, AnkiTmpl, ScriptInsertion, LabelText,
)

from .interface import make_interface, make_script

_meta_interfaces: List[Interface] = []
_meta_scripts: List[Tuple[str, MetaScript]] = []

# needs to be cast to int
ModelId = Union[int, str]

class InterfaceIsNotRegistered(Exception):
    pass

def make_and_register_interface(
    tag: str,
    getter: Callable[[str, ScriptStorage], ConcreteScript],
    setter: Callable[[str, ConcreteScript], Union[bool, ConcreteScript]],
    generator: Optional[Callable[[str, ScriptStorage, AnkiModel, AnkiTmpl, ScriptInsertion], Falsifiable(ScriptText)]] = None,
    label: Optional[Falsifiable(Callable[[str, ScriptStorage], LabelText])] = None,
    reset: Optional[Falsifiable(Callable[[str, ScriptStorage], ConcreteScript])] = None,
    deletable: Optional[Falsifiable(Callable[[str, ScriptStorage], bool])] = None,
    readonly: Optional[Union[List[ScriptKeys], ScriptStorage]] = None,
    store: Optional[Union[List[ScriptKeys], ScriptStorage]] = None,
) -> Interface:
    register_interface(make_interface(
        tag,
        getter,
        setter,
        generator,
        label,
        reset,
        deletable,
        readonly,
        store,
    ))

def register_interface(iface: Interface) -> None:
    _meta_interfaces.append(iface)


loose_interface = make_interface(
    tag = '__loose',
    getter = lambda id, storage: make_script(
        storage.name if storage.name is not None else '',
        storage.enabled if storage.enabled is not None else True,
        storage.type if storage.type is not None else 'js',
        storage.version if storage.version is not None else '',
        storage.description if storage.description is not None else '',
        storage.position if storage.position is not None else 'into_template',
        storage.conditions if storage.conditions is not None else [],
        storage.code if storage.code is not None else '',
    ),
    setter = lambda id, script: True,
    store = ['name', 'type', 'version', 'description', 'enabled', 'conditions', 'position', 'code'],
    readonly = [],
    reset = False,
    deletable = True,
    generator = lambda id, storage, model, tmpl, pos: '',
)

def get_interface(tag: str) -> Interface:
    try:
        return next(filter(lambda v: v.tag == tag, _meta_interfaces))
    except StopIteration:
        return loose_interface

def has_interface(tag: str) -> bool:
    return True if get_interface(tag) else False

##############

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
