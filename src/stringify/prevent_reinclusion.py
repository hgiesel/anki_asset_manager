from .package import package
from .stringify import gen_data_attributes
from .script_data import stringify_script_data

prevent_reinclusion = package(
    gen_data_attributes("Prevent reinclusion", "v0.1"),
    "js",
    "",
    """
    var ankiAms = document.querySelectorAll('#anki-am')
  if (ankiAms.length > 1) {
    for (const am of Array.from(ankiAms).slice(0, -1)) {
      am.outerHTML = ''
  }
}""".strip(),
    [],
)


def get_prevent_reinclusion(indent_size):
    return stringify_script_data(prevent_reinclusion, indent_size, True)
