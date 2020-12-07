import re

from typing import List, Optional

from aqt import mw

from ..config_types import HTML, HTMLSetting, ScriptSetting
from ..stringify import stringify_for_template, get_condition_parser

from .common import write_model_template


def find_valid_fragment(
    fragments: List[HTML], label: str, cond_parser
) -> Optional[HTML]:
    for frag in fragments:
        conded = cond_parser(frag.conditions)

        if frag.label == label and conded[0]:
            return frag

    return None


def gather_numerical_tags(text: str):
    return list(reversed(list(re.finditer(r"\{\{%(\d+)\}\}", text))))


def gather_tags(text: str):
    return list(reversed(list(re.finditer(r"\{\{%(\w+)(?::(.*?))?\}\}", text))))


squote = re.compile(r"^'(.*?)'\s*?(?:,|$)")
dquote = re.compile(r'^"(.*?)"\s*?(?:,|$)')
naked = re.compile(r"^([^,]+)(?:,|$)")


def match_tag_argument(text):
    if m := re.match(squote, text):
        return text[m.end() : len(text)], m.group(1)
    elif m := re.match(dquote, text):
        return text[m.end() : len(text)], m.group(1)
    elif m := re.match(naked, text):
        return text[m.end() : len(text)], m.group(1).rstrip()

    return None


def get_tag_arguments(text: Optional[str]):
    result = []

    while text:
        next = match_tag_argument(text.lstrip())

        if not next:
            break

        text = next[0]
        result.append(next[1])

    return result


def get_special_parser(scripts, model, cardtype_name, idx, position):
    def inner_parser(keyword):
        if keyword == "idx":
            return str(idx)

        if keyword == "cardidx":
            return re.search(r"\d*$", cardtype_name)[0]

        elif keyword == "scripts":
            return stringify_for_template(
                scripts,
                model["name"],
                model["id"],
                cardtype_name,
                position,
            )

        return ""

    return inner_parser


def evaluate_numerical(fragment: str, arguments: List[str]):
    text = fragment
    inner_tags = gather_numerical_tags(text)

    for match in inner_tags:
        keyword = match.group(1)

        try:
            numerical = int(keyword)
            replacement = arguments[numerical - 1]

        except (ValueError, IndexError):
            replacement = ""

        text = replacement.join(
            [
                text[0 : match.start()],
                text[match.end() : len(text) + 1],
            ]
        )

    return text


def indent(text: str, amount: int) -> str:
    """indent according to amount, but skip first line"""

    return "\n".join(
        [
            amount * " " + line if id > 0 else line
            for id, line in enumerate(text.split("\n"))
        ]
    )


def find_correct_indent(match) -> int:
    before = match.string[0 : match.start()]
    before_reversed = before[::-1]
    next_newline = before_reversed.find("\n")

    return (
        next_newline
        if next_newline >= 0 and re.match(r"^\s+$", before_reversed[0:next_newline])
        else 0
    )


def evaluate_fragment(
    fragments: List[HTML],
    entrance: str,
    cond_parser,
    special_parser,
) -> Optional[str]:
    base = find_valid_fragment(fragments, entrance, cond_parser)

    text = base.code
    inner_tags = gather_tags(text)
    iterations = 0

    while len(inner_tags) != 0 and iterations < 50:
        for match in inner_tags:
            keyword = match.group(1)
            arguments = get_tag_arguments(match.group(2))

            if keyword[0].islower():
                replacement = special_parser(keyword)

            elif keyword[0].isupper():
                fragment = find_valid_fragment(fragments, keyword, cond_parser)
                replacement = (
                    evaluate_numerical(fragment.code, arguments) if fragment else ""
                )

            else:
                replacement = ""

            replacement = indent(replacement, find_correct_indent(match))

            text = replacement.join(
                [
                    text[0 : match.start()],
                    text[match.end() : len(text) + 1],
                ]
            )

        inner_tags = gather_tags(text)
        iterations += 1

    return text


def setup_full(model_id: int, html: HTMLSetting, scripts: ScriptSetting):
    model = mw.col.models.get(model_id)

    for idx, template in enumerate(model["tmpls"]):
        # anki uses qfmt and afmt in model objects
        # I use question and answer
        cardtype_name = template["name"]

        for fmt in ["qfmt", "afmt"]:
            entrance = "Front" if fmt == "qfmt" else "Back"
            position = "question" if fmt == "qfmt" else "answer"

            conds = get_condition_parser(cardtype_name, position)
            specials = get_special_parser(
                scripts, model, cardtype_name, idx + 1, position
            )
            result = evaluate_fragment(html.fragments, entrance, conds, specials)

            if result:
                write_model_template(template, fmt, result)

    mw.col.models.save(model, True)
