def package(tag: str, subtype: str, label: str, code: str, conditions: list) -> object:
    return {
        "tag": tag,
        "type": subtype,
        "label": label,
        "code": code,
        "conditions": conditions,
    }


# filename is required for both insertion into template and creation of file
def package_for_external(
    tag: str, subtype: str, filename: str, code: str, conditions: list
) -> object:
    return {
        "tag": tag,
        "type": subtype,
        "src": filename,
        "code": code,
        "conditions": conditions,
    }
