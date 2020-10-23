from typing import Optional, Callable, Union, List, Literal
from dataclasses import dataclass, replace

################################ simple types

ScriptType = Literal['js', 'esm', 'css']

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
    'label',
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

################################ for scripts

dataclass(frozen=True)
class Script:
    pass

@dataclass(frozen=True)
class ConcreteScript(Script):
    name: str
    enabled: bool
    type: ScriptType
    label: str
    version: str
    description: str
    position: ScriptPosition
    conditions: list
    code: str

@dataclass(frozen=True)
class ScriptStorage:
    name: Optional[str]
    enabled: Optional[bool]
    type: Optional[ScriptType]
    label: Optional[str]
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

@dataclass(frozen=True)
class ScriptSetting:
    enabled: bool
    insert_stub: bool
    indent_size: int
    scripts: List[Script]

################################ for interfaces

@dataclass(frozen=True)
class ScriptBool:
    name: bool
    enabled: bool
    type: bool
    label: bool
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
    autodelete: Falsifiable(Callable[[str, ScriptStorage], bool])

    # list of values that are readonly
    readonly: ScriptBool
    # list of values or stored in `storage` field
    store: ScriptBool

################################ default settings for safenav

DEFAULT_SETTING = ScriptSetting(False, False, 4, [])

DEFAULT_CONCRETE_SCRIPT = ConcreteScript(
    'Example Script',
    False,
    'js',
    '',
    'v0.1',
    'This is an example script',
    'into_template',
    [],
    'console.log(\'Hello, World!\')',
)

DEFAULT_META_SCRIPT = MetaScript(
    'I_DONT_EXIST',
    'I_DONT_EXIST',
    ScriptStorage(False, False, False, False, False, False, False, False),
)

################################ for scripts


dataclass(frozen=True)
class HTML:
    pass

@dataclass(frozen=True)
class ConcreteHTML(HTML):
    name: str
    enabled: bool
    label: str
    version: str
    description: str
    conditions: list
    code: str

@dataclass(frozen=True)
class HTMLBool(HTML):
    name: bool
    enabled: bool
    label: bool
    version: bool
    description: bool
    conditions: bool
    code: bool

@dataclass(frozen=True)
class HTMLSetting:
    enabled: bool
    fragments: List[HTML]

DEFAULT_CONCRETE_HTML_FRONT = ConcreteHTML(
    'FrontSide',
    True,
    'Front',
    'v1',
    'This is the entrance for the front side',
    [],
    '{{Front}}\n\n{{%scripts}}',
)

DEFAULT_CONCRETE_HTML_BACK = ConcreteHTML(
    'BackSide',
    True,
    'Back',
    'v1',
    'This is the entrance for the back side',
    [],
    '{{FrontSide}}\n\n<hr id="answer">\n\n{{Back}}\n\n{{%scripts}}',
)

DEFAULT_CONCRETE_HTML = ConcreteHTML(
    'New Fragment',
    True,
    'Fragment',
    'v1',
    'This is my custom fragment',
    [],
    '<div>\n    Hello world!\n</div>\n',
)

DEFAULT_HTML_SETTING = HTMLSetting(False, [
    DEFAULT_CONCRETE_HTML_FRONT,
    DEFAULT_CONCRETE_HTML_BACK,
])
