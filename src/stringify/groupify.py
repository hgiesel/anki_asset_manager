from aqt.utils import showText
from itertools import groupby

from ..config_types import Script, ConcreteScript, MetaScript
from ..lib.registrar import get_interface

def safe_concrete(script: Script) -> ConcreteScript:
    if isinstance(script, ConcreteScript):
        return script

    iface = get_interface(script.tag)
    return iface.getter(script.id, script.storage)

def groupify(scripts):
    sorted_scripts = sorted(map(safe_concrete, scripts), key = lambda script: script.label)
    grouped = groupby(sorted_scripts, key = lambda script: script.label)

    showText(f'{grouped=}')
    return grouped
