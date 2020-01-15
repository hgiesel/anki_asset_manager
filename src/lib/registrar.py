from typing import Optional, List, Tuple

from .types import SMInterface, SMMetaScript
from .interface import make_meta_script

_meta_interfaces: List[SMInterface] = []
_meta_scripts: List[Tuple[str, SMMetaScript]] = []

class SMInterfaceIsNotRegistered(Exception):
    pass

def register_interface(iface: SMInterface) -> None:
    _meta_interfaces.append(iface)

def register_meta_script(model_name: str, meta_script: SMMetaScript) -> None:
    if has_interface(meta_script.tag):
        _meta_scripts.append((model_name, meta_script,))
    else:
        raise SMInterfaceIsNotRegistered(
            'You tried to register a meta script for a non existing interface. '
            'Make sure to register the interface first.'
        )

def get_interface(tag: str) -> Optional[SMInterface]:
    try:
        return next(filter(lambda v: v.tag == tag, _meta_interfaces))
    except StopIteration:
        return None

def get_meta_scripts(model_name: Optional[str] = None) -> List[SMMetaScript]:
    return [ms[1] for ms in _meta_scripts if ms[0] == model_name or model_name is None]

def has_interface(tag: str) -> bool:
    return True if get_interface(tag) else False

def meta_script_is_registered(model_name: str, tag: str, id: str) -> bool:
    try:
        return next(filter(lambda v: v[0] == model_name and v[1].tag == tag and v[1].id == id, _meta_scripts))
    except StopIteration:
        return False
