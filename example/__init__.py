from aqt import mw
from aqt.gui_hooks import profile_did_open

from .utils import find_addon_by_name

script_name = 'MyAwesomeScript'
version = 'v1.0'
description = 'This is my awesome script!'

am = find_addon_by_name('Asset Manager')

if am:
    ami = __import__(am).src.lib.interface
    amr = __import__(am).src.lib.registrar

def get_script() -> str:
    from pathlib import Path
    from os.path import dirname, realpath

    filepath = Path(dirname(realpath(__file__)), f'{script_name}.js')

    with open(filepath, 'r') as file:
        return file.read().strip()

def setup_script():
    if not am:
        return

    script = get_script()

    my_interface = ami.make_interface(
        # The name of script tag
        # Multiple scripts can be registered under the same tag
        # Scripts under one tag share one *interface*: rules for setting, getting, generation, stored fields, readonly fields, etc.
        tag = f"{script_name}_tag",

        # What happens when the user tries to receive the script
        # This is is used for displaying the script in the tag window
        # the code is not necessarily the code that is actually inserted into the template: for that, see `generator`
        # however the conditions are used for calculating whether to insert
        getter = lambda id, storage: ami.make_script(
            script_name,
            storage.enabled if storage.enabled is not None else True,
            'js',
            version,
            description,
            storage.position if storage.position is not None else 'into_template',
            storage.conditions if storage.conditions is not None else [],
            storage.code if storage.code is not None else script,
        ),

        # What happens when the user commits new changes to the script
        # Can be used for internal computation
        # returns a bool or ami.Script.
        # if returns True all fields defined in `store` are stored
        # if returns False no fields are stored ever
        # if returns ami.Script, this Script is used for saving, otherwise it's the same as the argument
        setter = lambda id, script: True,

        # Collection of fields that are stored by Script Manager
        store = ['enabled', 'code', 'position', 'conditions'],
        # Collection of fields that are read-only
        readonly = ['name', 'type', 'version', 'description'],

        # Change the code that is showed in the script window
        # By default it is "your_tag: your_id"
        # label = lambda id, storage: your code that returns str

        # Change the behavior when deleting the script
        # By default your script is not deletable
        # deletable = lambda id, storage: your code that returns bool (whether to delete or not)

        # Change the behavior when resetting the script
        # By default your script is reset to the getter function with an empty storage
        # this reset function does not reset the enabled status or the conditions
        reset = lambda id, storage: ami.make_script(
            script_name,
            storage.enabled if storage.enabled else True,
            'js',
            version,
            description,
            'into_template',
            storage.conditions if storage.conditions is not None else [],
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

    amr.register_interface(my_interface)

def install_script():
    # create the meta script which points to your interface
    my_meta_script = ami.make_meta_script(
        # this is the tag your interface above is registered on!
        f"{script_name}_tag",
        # your id: you can register an id only once per model per tag
        f"{script_name}_id",
    )

    # insert the script for every model
    for model_id in mw.col.models.ids():
        amr.register_meta_script(
            model_id,
            my_meta_script,
        )

if am:
    setup_script()
    profile_did_open.append(install_script)
