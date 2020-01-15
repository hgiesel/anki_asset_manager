from typing import Optional, List
from .types import SMInterface, SMMetaScript

_meta_interfaces = []
_meta_scripts = []

def register_interface(iface: SMInterface) -> None:
    _meta_interfaces.append(iface)

def get_interface(tag: str) -> Optional[SMInterface]:
    try:
        return next(filter(lambda v: v.tag == tag, _meta_interfaces))
    except StopIteration:
        return None

def has_interface(tag: str) -> bool:
    return True if get_interface(tag) else False

def add_meta_script(model_name: str, tag: str, id: str) -> None:
    if get_interface(tag) != None:
        _meta_scripts.append((model_name, SMMetaScript(tag, id),))

def get_meta_scripts(model_name: Optional[str] = None) -> List[SMMetaScript]:
    return [ms[1] for ms in _meta_scripts if ms[0] == model_name or model_name is None]

def meta_script_is_registered(model_name: str, tag: str, id: str) -> bool:
    try:
        return next(filter(lambda v: v[0] == model_name and v[1].tag == tag and v[1].id == id, _meta_scripts))
    except StopIteration:
        return False
