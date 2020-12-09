from typing import Union, Tuple

from ..lib.registrar import get_reducer
from ..config_types import ScriptInsertion

from .condition_parser import stringify_conds
from .indent import indent_lines
from .package import package


def wrap_code(code: str, conditions: Union[bool, list]):
    if ((type(conditions) is bool) and conditions) or len(conditions) == 0:
        return code

    else:
        main_code = "\n".join([f"    {line}" for line in code.split("\n")])
        return f"if ({stringify_conds(conditions)}) {{\n{main_code}\n}}"


def stringify_script_data(sd: object, indent_size: int, in_html: bool) -> str:
    srcTag = f" src=\"{sd['src']}\"" if "src" in sd else ""
    module = ' type="module"' if sd["type"] == "esm" else ""

    opening, closing = (
        (
            f'<script {sd["tag"]}{module}{srcTag}>',
            "</script>",
        )
        if in_html
        else (
            f'// {sd["tag"]}',
            "",
        )
    )

    wrapped_code = (
        "" if "src" in sd and in_html else wrap_code(sd["code"], sd["conditions"])
    )
    indented_code = indent_lines(wrapped_code, indent_size if in_html else 0)

    # avoid two empty new lines for external scripts
    opening, indented_code = (
        (
            f"{opening}\n",
            f"{indented_code}\n",
        )
        if len(indented_code) > 0
        else (opening, "")
    )

    return opening + indented_code + closing


def stringify_sd(
    sd: object, indent_size: int, in_html: bool
) -> Union[Tuple[str, str], str]:
    return (
        (sd["src"], stringify_script_data(sd, indent_size, in_html))
        if "src" in sd and not in_html
        else stringify_script_data(sd, indent_size, in_html)
    )


def merge_sd(key: str, sds: list):
    base = sds[0]  # Top script in list
    reducer = get_reducer(key)
    compiled = reducer.reducer([sd["code"] for sd in sds])

    return package(
        base["tag"],
        base["type"],
        key,
        compiled,
        base["conditions"],
    )
