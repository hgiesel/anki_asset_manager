from typing import Optional, List, Union, Tuple

from ...config_types import (
    MetaScript,
)

from .iface import has_interface


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
