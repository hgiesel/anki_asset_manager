from typing import Optional, List, Callable, Union

from ...config_types import (
    Interface,
    ConcreteScript,
    AnkiModel,
    AnkiTmpl,

    ScriptStorage,
    ScriptInsertion,
    ScriptText,
    LabelText,
    ScriptKeys,

    Falsifiable,
)

from ..interface import make_interface, make_script_v2


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

def _make_loose_interface(tag: str) -> Interface:
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
        return _make_loose_interface(tag)

def has_interface(tag: str) -> bool:
    try:
        next(filter(lambda v: v.tag == tag, _meta_interfaces))
        return True
    except StopIteration:
        return False
