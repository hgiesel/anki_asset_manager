from ..config_types import AnkiFmt


def write_model_template(template: object, fmt: AnkiFmt, value: str) -> bool:
    template[fmt] = value
