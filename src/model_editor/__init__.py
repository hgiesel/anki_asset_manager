from ..config_types import HTMLSetting, ScriptSetting

from .setup_scripts import setup_with_only_scripts
from .setup_html import setup_full

def setup_model(model_id: int, html: HTMLSetting, scripts: ScriptSetting):
    if html.enabled:
        setup_full(model_id, html, scripts)
    else:
        setup_with_only_scripts(model_id, scripts)
