from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class SMSetting:
    model_name: str
    enabled: bool
    insert_stub: bool
    indent_size: int
    scripts: list

dataclass(frozen=True)
class SMScript:
    pass

@dataclass(frozen=True)
class SMConcrScript(SMScript):
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
class SMMetaScript(SMScript):
    tag: str
    id: str
    storage: SMScriptStorage

################################

AnkiModel = str
AnkiTmpl = str
AnkiFmt = Literal['qfmt', 'afmt']
ScriptText = str
LabelText = str
Falsifiable = lambda t: Union[Literal[False], t]

@dataclass(frozen=True)
class SMInterface:
    # name for the type of the interface
    tag: str
    getter: Callable[[str, SMScriptStorage], SMConcrScript]
    # result is used for storing
    setter: Callable[[str, SMConcrScript], Union[bool, SMConcrScript]]
    generator: Callable[[str, SMScriptStorage, AnkiModel, AnkiTmpl, AnkiFmt], Falsifiable(ScriptText)]
    label: Falsifiable(Callable[[str, SMScriptStorage], LabelText])
    reset: Falsifiable(Callable[[str, SMScriptStorage], SMConcrScript])
    deletable: Falsifiable(Callable[[str, SMScriptStorage], bool])

    # list of values that are readonly
    readonly: SMScriptBool
    # list of values or stored in `storage` field
    store: SMScriptBool
