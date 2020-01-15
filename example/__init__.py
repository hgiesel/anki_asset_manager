from aqt import mw
from aqt.utils import showInfo

from .utils import find_addon_by_name

sm = find_addon_by_name('Script Manager')

if sm:
    smt = __import__(sm).src.lib.types
    smi = __import__(sm).src.lib.interface

    script_name = 'MyAwesomeScript'
    version = 'v1.0'
    description = 'This is my awesome script!'

    from pathlib import Path
    from os.path import dirname, realpath

    filepath = Path(f'{dirname(realpath(__file__))}', f'{script_name}.js')

    with open(filepath, 'r') as file:
        script = file.read().strip()

        smi.register_interface(
            smt.SMInterface(
                # The name of script tag
                # Multiple scripts can be registered under the same tag
                # Scripts under one tag share one *interface*: rules for setting, getting, generation, stored fields, readonly fields, etc.
                tag = f"{script_name}_tag",

                # What happens when the user tries to receive the script
                # This is is used for displaying the script in the tag window
                # the code is not necessarily the code that is actually inserted into the template: for that, see `generator`
                # however the conditions are used for calculating whether to insert
                getter = lambda id, storage: smt.SMScript(
                    storage.enabled if storage.enabled else True,
                    script_name,
                    version,
                    description,
                    storage.conditions if storage.conditions else [],
                    storage.code if storage.code else script,
                ),

                # What happens when the user commits new changes to the script
                # Can be used for internal computation
                # returns a bool or smi.SMScript.
                # if returns True all fields defined in `store` are stored
                # if returns False no fields are stored ever
                # if returns smi.SMScript, this SMScript is used for saving, otherwise it's the same as the argument
                setter = lambda id, script: True,

                # Collection of fields that are stored on the side of Script Manager
                store = ['enabled', 'code', 'conditions'],
                # Collection of fields that are readonly
                readonly = ['name', 'version', 'description'],

                # Change the code that is showed in the script window
                # By default is "your_tag: your_id"
                # label = lambda id, storage: your code that returns str

                # Change the behavior when deleting the script
                # By default your script is not deletable
                # deletable = lambda id, storage: your code that returns bool (whether to delete or not)

                # Change the behavior when resetting the script
                # By default your script is reset to the getter function with an empty storage
                # this reset function does not reset the enabled status or the conditions
                reset = lambda id, storage: smt.SMScript(
                    storage.enabled if storage.enabled else True,
                    script_name,
                    version,
                    description,
                    storage.conditions if storage.conditions else [],
                    script,
                ),
                # ...or...
                # reset = False (your code cannot be reset + reset button is hidden)

                # Change the behavior when generating the script that is ultimately inserted into the template
                # By default it uses `getter(id, storage).code`
                # model is the note type name, tmpl is the card type name, fmt is 'qfmt' (front) or 'afmt' (back)
                # if your return an empty str, it won't insert anything
                # generator = lambda id, storage, model, tmpl, fmt: your code that returns a str (that is then inserted into the template)
            )
        )

    def install_script():
        # insert the script for every model
        for model_name in mw.col.models.allNames():

            smi.add_meta_script(
                model_name,
                # the interface above is registered on the same name!
                f"{script_name}_tag",
                # your id: you can register an id only once per model per tag
                f"{script_name}_id",
            )

    from anki.hooks import addHook
    addHook('profileLoaded', install_script)
