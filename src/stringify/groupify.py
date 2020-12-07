from typing import List
from itertools import groupby

from ..config_types import Script, ConcreteScript, MetaScript
from ..lib.registrar import get_interface


def safe_concrete(script: Script) -> ConcreteScript:
    if isinstance(script, ConcreteScript):
        return script

    iface = get_interface(script.tag)
    return iface.getter(script.id, script.storage)


def get_script_data_label(sd: object) -> str:
    return sd["label"] if "label" in sd else ""


def groupify_external(scripts):
    sorted_scripts = sorted(
        map(safe_concrete, scripts), key=lambda script: script.label
    )
    grouped = groupby(sorted_scripts, key=lambda script: script.label)

    return grouped


def groupify_script_data(script_data: List[object]):
    sorted_scripts = sorted(script_data, key=get_script_data_label)
    grouped = groupby(sorted_scripts, key=get_script_data_label)

    return grouped
