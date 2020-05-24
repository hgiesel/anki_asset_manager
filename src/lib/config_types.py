from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class AMSetting:
    model_name: str
    enabled: bool
    insert_stub: bool
    indent_size: int
    scripts: list

dataclass(frozen=True)
class AMScript:
    pass

@dataclass(frozen=True)
class AMConcrScript(AMScript):
    enabled: bool
    name: str
    version: str
    description: str
    conditions: list
    code: str

################################

@dataclass(frozen=True)
class AMScriptBool:
    enabled: bool
    name: bool
    version: bool
    description: bool
    conditions: bool
    code: bool

@dataclass(frozen=True)
class AMScriptStorage:
    enabled: Optional[bool]
    name: Optional[str]
    version: Optional[str]
    description: Optional[str]
    conditions: Optional[list]
    code: Optional[str]

@dataclass(frozen=True)
class AMMetaScript(AMScript):
    tag: str
    id: str
    storage: AMScriptStorage

################################

AnkiModel = str
AnkiTmpl = str
AnkiFmt = Literal['qfmt', 'afmt']
ScriptText = str
LabelText = str
Falsifiable = lambda t: Union[Literal[False], t]

@dataclass(frozen=True)
class AMInterface:
    # name for the type of the interface
    tag: str
    getter: Callable[[str, AMScriptStorage], AMConcrScript]
    # result is used for storing
    setter: Callable[[str, AMConcrScript], Union[bool, AMConcrScript]]
    generator: Callable[[str, AMScriptStorage, AnkiModel, AnkiTmpl, AnkiFmt], Falsifiable(ScriptText)]
    label: Falsifiable(Callable[[str, AMScriptStorage], LabelText])
    reset: Falsifiable(Callable[[str, AMScriptStorage], AMConcrScript])
    deletable: Falsifiable(Callable[[str, AMScriptStorage], bool])

    # list of values that are readonly
    readonly: AMScriptBool
    # list of values or stored in `storage` field
    store: AMScriptBool
