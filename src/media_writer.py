from re import match
from os import listdir

from aqt import mw

from .config_types import ScriptSetting
from .stringify import stringify_for_external


def write_media(model_id: int, setting: ScriptSetting):
    needs_saving = False
    model = mw.col.models.get(model_id)

    external_scripts = stringify_for_external(
        setting,
        model["name"],
        model_id,
    )

    prefix_regex = f"^_am_{model_id}_"
    files = [file for file in listdir(mw.col.media.dir()) if match(prefix_regex, file)]
    mw.col.media.trash_files(files)

    for script in external_scripts:
        mw.col.media.write_data(script[0], script[1].encode())
