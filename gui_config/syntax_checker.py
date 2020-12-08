from aqt import mw
from aqt.webview import AnkiWebView
from aqt.utils import showInfo, showWarning


class SyntaxChecker(AnkiWebView):
    def __init__(self, parent):
        AnkiWebView.__init__(self, parent=parent, title="syntax_checker")

    def check(self, code: str) -> None:
        escaped = code.replace('"', '\\"').replace("\n", "\\n")

        self.eval(
            f"""
Terser.minify("{escaped}")
    .then(
        _result => pycmd("info::Success::No syntax error found"),
        error => pycmd(`warning::${{error.name}}::${{error.message}}::${{error.line}}::${{error.col}}`),
    )
"""
        )


def bridge_cmd(cmd: str) -> None:
    if cmd.startswith("info"):
        _, code, message = cmd.split("::")
        showInfo(f"{code}: {message}")
        return

    elif cmd.startswith("warning"):
        _, code, message, line, col = cmd.split("::")
        showWarning(f"{code}: {line}:{col}: {message}")
        return


def get_syntax_checker(parent) -> SyntaxChecker:
    syntax_checker = SyntaxChecker(parent)

    addon_package = mw.addonManager.addonFromModule(__name__)
    syntax_checker.stdHtml(
        "",
        js=[
            f"/_addons/{addon_package}/web/terser.js",
        ],
    )

    syntax_checker.set_bridge_command(bridge_cmd, parent)
    return syntax_checker
