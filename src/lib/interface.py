from .types import SMInterface, SMMetaScript, SMScriptBool

_meta_interfaces = []
_meta_scripts = []

def register_interface(
    # name for the type of the interface
    tag: str,
    # function (id, note type, e.g. 'Standard', card type, e.g. 'FromQuestion', 'qfmt' | 'afmt')
    generator: 'Callable[[id, model, tmpl, fmt]] -> str or False]',
    # getting a SMScript with id
    getter: 'Callable[[id, SMScriptStore] -> SMScript]',
    # setting a SMScript with id
    setter: 'Callable[[id, SMScript] -> None]',
    # if False then cannot be deleted, else, the function is called with id
    deleteable: False or 'Callable[[id, SMScript] -> None]',
    # list of values that are readonly
    # can contain: 'enabled', 'name', 'version', 'description', 'conditions', 'code'
    readonly: SMScriptBool,
    # list of values that are stored in `store` field
    # can contain: 'enabled', 'name', 'version', 'description', 'conditions', 'code'
    store: SMScriptBool,
):
    _meta_interfaces.append(SMInterface(
        tag,
        generator,
        getter,
        setter,
        deleteable,
        readonly,
        store,
    ))

def get_interface(tag):
    try:
        return next(filter(lambda v: v.tag == tag, _meta_interfaces))
    except:
        return None

def has_interface(tag):
    return True if get_interface(tag) else False

def add_meta_script(tag, id):
    if get_interface(tag) != None:
        _meta_scripts.append(SMMetaScript(tag, id))

def get_meta_scripts():
    return _meta_scripts

from aqt.utils import showInfo
showInfo(str(_meta_interfaces))
