import attr

@attr.s(slots=True, frozen=True)
class SMSetting:
    model_name: str = attr.ib()
    scripts: list = attr.ib()

@attr.s(slots=True, frozen=True)
class SMScript:
    enabled: bool = attr.ib(False)
    name: str = attr.ib('')
    version: str = attr.ib('')
    description: str = attr.ib('')
    conditions: list = attr.ib([])
    code: str = attr.ib('')

################################

@attr.s(slots=True, frozen=True)
class SMInterface:
    tag: str = attr.ib()
    generator = attr.ib()
    getter = attr.ib()
    setter = attr.ib()
    deleteable: bool or 'function' = attr.ib()
    readonly: SMScriptBool = attr.ib(default = SMScriptBool())
    store: SMScriptBool = attr.ib(default = SMScriptBool())

################################

@attr.s(slots=True, frozen=True)
class SMMetaScript:
    tag: str = attr.ib()
    id: str = attr.ib()
    storage: SMScriptStore = attr.ib(default=SMScriptStore())

@attr.s(slots=True, frozen=True)
class SMScriptBool:
    enabled: bool = attr.ib(False)
    name: bool = attr.ib(False)
    version: bool = attr.ib(False)
    description: bool = attr.ib(False)
    conditions: bool = attr.ib(False)
    code: bool = attr.ib(False)

@attr.s(slots=True, frozen=True)
class SMScriptStore:
    enabled: bool = attr.ib(default=None)
    name: str = attr.ib(default=None)
    version: str = attr.ib(default=None)
    description: str = attr.ib(default=None)
    conditions: list = attr.ib(default=None)
    code: str = attr.ib(default=None)
