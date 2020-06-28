from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

################################ simple types

ScriptType = Literal['js', 'css']

Position = Literal['external', 'head', 'body']
ScriptPosition = Union[Position, Literal['into_template']]

AnkiFmt = Literal['qfmt', 'afmt']
Fmt = Literal['question', 'answer']
ScriptInsertion = Union[Position, Fmt]

ScriptText = str
ScriptKeys = Literal[
    'name',
    'enabled',
    'type',
    'version',
    'description',
    'position',
    'conditions',
    'code',
]

LabelText = str
AnkiModel = str
AnkiTmpl = str

Falsifiable = lambda t: Union[Literal[False], t]

################################ for concr scripts

@dataclass(frozen=True)
class Setting:
    enabled: bool
    insert_stub: bool
    indent_size: int
    scripts: list

dataclass(frozen=True)
class Script:
    pass

@dataclass(frozen=True)
class ConcreteScript(Script):
    name: str
    enabled: bool
    type: ScriptType
    version: str
    description: str
    position: ScriptPosition
    conditions: list
    code: str

################################ for meta scripts

@dataclass(frozen=True)
class ScriptStorage:
    name: Optional[str]
    enabled: Optional[bool]
    type: Optional[ScriptType]
    version: Optional[str]
    description: Optional[str]
    position: Optional[ScriptPosition]
    conditions: Optional[list]
    code: Optional[str]

@dataclass(frozen=True)
class MetaScript(Script):
    tag: str
    id: str
    storage: ScriptStorage

################################ for interfaces

@dataclass(frozen=True)
class ScriptBool:
    name: bool
    enabled: bool
    type: bool
    version: bool
    description: bool
    position: bool
    conditions: bool
    code: bool

@dataclass(frozen=True)
class Interface:
    # name for the type of the interface
    tag: str
    getter: Callable[[str, ScriptStorage], ConcreteScript]
    # result is used for storing
    setter: Callable[[str, ConcreteScript], Union[bool, ConcreteScript]]
    generator: Callable[[str, ScriptStorage, AnkiModel, AnkiTmpl, ScriptInsertion], Falsifiable(ScriptText)]
    label: Falsifiable(Callable[[str, ScriptStorage], LabelText])
    reset: Falsifiable(Callable[[str, ScriptStorage], ConcreteScript])
    deletable: Falsifiable(Callable[[str, ScriptStorage], bool])

    # list of values that are readonly
    readonly: ScriptBool
    # list of values or stored in `storage` field
    store: ScriptBool

################################ default settings for safenav

DEFAULT_SETTING = Setting(False, False, 4, [])

DEFAULT_CONCRETE_SCRIPT = ConcreteScript(
    False,
    'js',
    'Example Script',
    'v0.1',
    'This is an example script',
    'body',
    [],
    'console.log(\'Hello, World\')',
)

DEFAULT_META_SCRIPT = MetaScript(
    'I_DONT_EXIST',
    'I_DONT_EXIST',
    ScriptStorage(False, False, False, False, False, False, False, False),
)
