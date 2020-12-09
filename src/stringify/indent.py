def indent(line, indentation):
    return indentation + line if len(line) > 0 else line


def indent_lines(text: str, indent_size: int) -> str:
    return "\n".join([indent(line, indent_size * " ") for line in text.split("\n")])
