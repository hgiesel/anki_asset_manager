import attr

@attr.s(slots=True, frozen=True)
class SMSetting:
    model_name: str = attr.ib()
    scripts: list = attr.ib()

@attr.s(slots=True, frozen=True)
class SMScript:
    enabled: bool = attr.ib()
    name: str = attr.ib()
    version: str = attr.ib()
    description: str = attr.ib()
    conditions: list = attr.ib()
    code: str = attr.ib()
