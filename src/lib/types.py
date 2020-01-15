from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class SMSetting:
    model_name: str
    enabled: bool
    indent_size: int
    scripts: list

@dataclass(frozen=True)
class SMConcrScript:
    enabled: bool
    name: str
    version: str
    description: str
    conditions: list
    code: str

################################

@dataclass(frozen=True)
class SMScriptBool:
    enabled: bool
    name: bool
    version: bool
    description: bool
    conditions: bool
    code: bool

@dataclass(frozen=True)
class SMScriptStorage:
    enabled: Optional[bool]
    name: Optional[str]
    version: Optional[str]
    description: Optional[str]
    conditions: Optional[list]
    code: Optional[str]

@dataclass(frozen=True)
class SMMetaScript:
    tag: str
    id: str
    storage: SMScriptStorage

################################

anki_model = str
anki_tmpl = str
anki_fmt = Literal['qfmt', 'afmt']
script_text = str
label_text = str

@dataclass(frozen=True)
class SMInterface:
    # name for the type of the interface
    tag: str
    getter: Callable[[str, SMScriptStorage], SMConcrScript]
    # result is used for storing
    setter: Callable[[str, SMConcrScript], Union[bool, SMConcrScript]]
    generator: Callable[[str, SMScriptStorage, anki_model, anki_tmpl, anki_fmt], Union[script_text, Literal[False]]]
    label: Union[Literal[False], Callable[[str, SMScriptStorage], label_text]]
    reset: Union[Literal[False], Callable[[str, SMScriptStorage], SMConcrScript]]
    deletable: Union[Literal[False], Callable[[str, SMScriptStorage], bool]]

    # list of values that are readonly
    readonly: SMScriptBool
    # list of values or stored in `storage` field
    store: SMScriptBool
