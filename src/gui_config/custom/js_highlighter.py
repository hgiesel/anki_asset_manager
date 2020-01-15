from aqt import QRegExp, QColor, QTextCharFormat, QFont, QSyntaxHighlighter, Qt

class JSHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JSHighlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontStyleHint(QFont.Monospace)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = [
            "\\bfunction\\b",
            "\\bclass\\b",

            "\\bvar\\b",
            "\\blet\\b",
            "\\bconst\\b",

            "\\bbreak\\b",
            "\\bcase\\b",
            "\\bcatch\\b",
            "\\bcontinue\\b",
            "\\bdebugger\\b",
            "\\bdefault\\b",
            "\\bdelete\\b",
            "\\bdo\\b",
            "\\belse\\b",
            "\\bfor\\b",
            "\\bif\\b",
            "\\bin\\b",
            "\\binstanceof\\b",
            "\\bnew\\b",
            "\\breturn\\b",
            "\\bswitch\\b",
            "\\bthis\\b",
            "\\bthrow\\b",
            "\\btry\\b",
            "\\btypeof\\b",
            "\\bvoid\\b",
            "\\bwhile\\b",
            "\\bwith\\b",
            "\\benum\\b",
            "\\bexport\\b",
            "\\bextends\\b",
            "\\bimport\\b",
            "\\bsuper\\b",
            "\\bimplements\\b",
            "\\binterface\\b",
            "\\bpackage\\b",
            "\\bprivate\\b",
            "\\bprotected\\b",
            "\\bpublic\\b",
            "\\bstatic\\b",
            "\\byield\\b",
        ]

        self.highlightingRules = [
            (QRegExp(pattern), keywordFormat)
            for pattern
            in keywordPatterns
        ]

        classFormat = QTextCharFormat()
        classFormat.setFontWeight(QFont.Bold)
        classFormat.setFontStyleHint(QFont.Monospace)
        classFormat.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("\\bQ[A-Za-z]+\\b"), classFormat))

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setFontStyleHint(QFont.Monospace)
        singleLineCommentFormat.setForeground(Qt.red)
        self.highlightingRules.append((QRegExp("//[^\n]*"), singleLineCommentFormat))

        multiLineCommentFormat = QTextCharFormat()
        multiLineCommentFormat.setFontStyleHint(QFont.Monospace)
        multiLineCommentFormat.setForeground(Qt.red)
        self.multiLineCommentFormat = multiLineCommentFormat

        numberFormat = QTextCharFormat()
        numberFormat.setFontStyleHint(QFont.Monospace)
        numberFormat.setForeground(Qt.cyan)
        self.highlightingRules.append((QRegExp("\\b\\d+\\b"), numberFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(Qt.darkGreen)
        quotationFormat.setFontStyleHint(QFont.Monospace)
        self.highlightingRules.append((QRegExp('".*"'), quotationFormat))
        self.highlightingRules.append((QRegExp("'.*'"), quotationFormat))
        self.highlightingRules.append((QRegExp('`.*`'), quotationFormat))

        functionFormat = QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setFontStyleHint(QFont.Monospace)
        functionFormat.setForeground(Qt.blue)
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"), functionFormat))

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength);
