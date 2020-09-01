from typing import Union


def map_truth_value_to_icon(b: Union[bool, str]) -> str:
    if b == True:
        return 'yes'
    elif b == False:
        return 'no'
    else:
        return b

def script_type_to_gui_text(txt: str) -> str:
    if txt == 'js':
        return 'JavaScript'
    elif txt == 'css':
        return 'CSS'

def pos_to_script_type(pos: int) -> str:
    if pos == 0:
        return 'js'
    elif pos == 1:
        return 'css'

def script_position_to_gui_text(txt: str) -> str:
    if txt == 'external':
        return 'As External Document'
    elif txt == 'head':
        return 'Document Head'
    elif txt == 'body':
        return 'Document Body'
    elif txt == 'into_template':
        return 'Into Template'

def pos_to_script_position(pos: int) -> str:
    if pos == 0:
        return 'external'
    elif pos == 1:
        return 'head'
    elif pos == 2:
        return 'body'
    elif pos == 3:
        return 'into_template'
