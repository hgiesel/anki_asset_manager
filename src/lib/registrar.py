from typing import Optional, List, Tuple

from .config_types import AMInterface, AMMetaScript
from .interface import make_meta_script

_meta_interfaces: List[AMInterface] = []
_meta_scripts: List[Tuple[str, AMMetaScript]] = []

class AMInterfaceIsNotRegistered(Exception):
    pass

def register_interface(iface: AMInterface) -> None:
    _meta_interfaces.append(iface)

def get_interface(tag: str) -> Optional[AMInterface]:
    try:
        return next(filter(lambda v: v.tag == tag, _meta_interfaces))
    except StopIteration:
        return None

def has_interface(tag: str) -> bool:
    return True if get_interface(tag) else False

##############

def register_meta_script(model_name: str, meta_script: AMMetaScript) -> None:
    if has_interface(meta_script.tag):
        _meta_scripts.append((model_name, meta_script,))
    else:
        raise AMInterfaceIsNotRegistered(
            'You tried to register a meta script for a non existing interface. '
            'Make sure to register the interface first.'
        )

def deregister_meta_script(model_name: str, meta_script: AMMetaScript) -> bool:
    if has_interface(meta_script.tag):
        try:
            found = next(filter(lambda v: (
                v[1][0] == model_name
                and v[1][1].tag == meta_script.tag
                and v[1][1].id == meta_script.id
            ), enumerate(_meta_scripts)))

            _meta_scripts.pop(found[0])
            return True

        except StopIteration:
            return False

    else:
        raise AMInterfaceIsNotRegistered(
            'You tried to register a meta script for a non existing interface. '
            'Make sure to register the interface first.'
        )

def get_meta_scripts(model_name: Optional[str] = None) -> List[AMMetaScript]:
    return [ms[1] for ms in _meta_scripts if ms[0] == model_name or model_name is None]

def meta_script_is_registered(model_name: str, tag: str, id: str) -> bool:
    try:
        return next(filter(lambda v: v[0] == model_name and v[1].tag == tag and v[1].id == id, _meta_scripts))
    except StopIteration:
        return False
