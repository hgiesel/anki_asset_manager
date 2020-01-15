import attr

@attr.s(slots=True, frozen=True)
class SMSetting:
    model_name: str = attr.ib()
    enabled: bool = attr.ib()
    indent_size: int = attr.ib()
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
class SMScriptBool:
    enabled: bool = attr.ib(False)
    name: bool = attr.ib(False)
    version: bool = attr.ib(False)
    description: bool = attr.ib(False)
    conditions: bool = attr.ib(False)
    code: bool = attr.ib(False)

@attr.s(slots=True, frozen=True)
class SMScriptStorage:
    enabled: bool = attr.ib(default=None)
    name: str = attr.ib(default=None)
    version: str = attr.ib(default=None)
    description: str = attr.ib(default=None)
    conditions: list = attr.ib(default=None)
    code: str = attr.ib(default=None)

@attr.s(slots=True, frozen=True)
class SMMetaScript:
    tag: str = attr.ib()
    id: str = attr.ib()
    storage: SMScriptStorage = attr.ib(default=SMScriptStorage())

################################

def list_to_sm_script_bool(vals):
    return (
        vals
        if type(vals) == SMScriptBool
        else attr.evolve(SMScriptBool(), **dict([(key, True) for key in vals]))
    )

@attr.s(slots=True, frozen=True)
class SMInterface:
    # name for the type of the interface
    tag: str = attr.ib()
    getter: 'Callable[[id, SMScriptStorage] -> SMScript]' = attr.ib()
    # setting a SMScript with id
    setter: 'Callable[[id, SMScript] -> None]' = attr.ib()

    # function (id, note type, e.g. 'Standard', card type, e.g. 'FromQuestion', 'qfmt' | 'afmt')
    generator: 'Callable[[id, SMScriptStorage, model, tmpl, fmt]] -> str or False]' = attr.ib()
    @generator.default
    def __generator_default(self):
        return lambda id, storage, _model, _tmpl, _fmt: self.getter(id, storage).code

    label: False or 'Callable[[id, SMScriptStorage] -> None]' = attr.ib()
    @label.default
    def __label_default(self):
        return lambda id, _storage: f"{self.tag}: {id}"

    reset: False or 'Callable[[id, SMScriptStorage] -> SMScript]' = attr.ib()
    @reset.default
    def __reset_default(self):
        return lambda id, _storage: self.getter(id, SMScriptBool())

    deletable: False or 'Callable[[id, SMScriptStorage] -> Bool]' = attr.ib()
    @reset.deletable
    def __reset_default(self):
        return lambda _id, _storage: False

    # list of values that are readonly; or stored in `storage` field
    # can contain: 'enabled', 'name', 'version', 'description', 'conditions', 'code'
    readonly: SMScriptBool = attr.ib(converter=list_to_sm_script_bool, default = SMScriptBool())
    store: SMScriptBool = attr.ib(converter=list_to_sm_script_bool, default = SMScriptBool())
