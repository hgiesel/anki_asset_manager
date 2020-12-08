from anki.models import NoteType

from ..config_types import AnkiFmt


def write_model_template(template: NoteType, fmt: AnkiFmt, value: str) -> bool:
    template[fmt] = value
