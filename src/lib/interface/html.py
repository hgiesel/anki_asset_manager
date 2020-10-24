from typing import Optional, List
from dataclasses import replace

from ...config_types import (
    HTMLSetting,
    HTMLBool,
    ConcreteHTML,
)

def make_html_setting(
    enabled: bool,
    fragments: list,
) -> HTMLSetting:
    return HTMLSetting(
        enabled,
        fragments,
    )

def make_html_bool(
    name: Optional[bool] = None,
    enabled: Optional[bool] = None,
    label: Optional[bool] = None,
    version: Optional[bool] = None,
    description: Optional[bool] = None,
    conditions: Optional[bool] = None,
    code: Optional[bool] = None,
) -> HTMLBool:
    return HTMLBool(
        name if name is not None else False,
        enabled if enabled is not None else False,
        label if label is not None else False,
        version if version is not None else False,
        description if description is not None else False,
        conditions if conditions is not None else False,
        code if code is not None else False,
    )

def __list_to_html_bool(vals: List[str]) -> HTMLBool:
    return replace(
        make_html_bool(),
        **dict([(key, True) for key in vals])
    )

def make_fragment(
    name: str,
    enabled: bool,
    label: str,
    version: str,
    description: str,
    conditions: list,
    code: str,
) -> ConcreteHTML:
    return ConcreteHTML(
        name,
        enabled,
        label,
        version,
        description,
        conditions,
        code,
    )
