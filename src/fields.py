from aqt.gui_hooks import fields_did_rename_field, fields_did_delete_field
from aqt.utils import showText


def rename_in_assets(fields, field, name):
    pass


def delete_in_assets(fields, field):
    pass


def init_fields():
    fields_did_rename_field.append(rename_in_assets)
    fields_did_delete_field.append(delete_in_assets)
