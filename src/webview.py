from aqt.gui_hooks import webview_will_set_content

from .lib.webview_hook import append_scripts

def setup_webview_hook():
    webview_will_set_content.append(append_scripts)
