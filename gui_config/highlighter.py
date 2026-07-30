from aqt.qt import (
    QRegularExpression as QRegExp,
    QRegularExpression,
    QColor,
    QTextCharFormat,
    QFont,
    QSyntaxHighlighter,
    Qt,
)
from aqt import mw


class JSHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JSHighlighter, self).__init__(parent)

        is_night_mode = mw.pm.night_mode()

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor(Qt.GlobalColor.cyan if is_night_mode else Qt.GlobalColor.blue))
        keywordFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        keywordFormat.setFontWeight(QFont.Weight.Bold)

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
            (QRegExp(pattern), keywordFormat) for pattern in keywordPatterns
        ]

        classFormat = QTextCharFormat()
        classFormat.setFontWeight(QFont.Weight.Bold)
        classFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        classFormat.setForeground(QColor(Qt.GlobalColor.magenta if is_night_mode else Qt.GlobalColor.darkMagenta))
        self.highlightingRules.append((QRegExp("\\bQ[A-Za-z]+\\b"), classFormat))

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        singleLineCommentFormat.setForeground(QColor(Qt.GlobalColor.red if is_night_mode else Qt.GlobalColor.darkRed))
        self.highlightingRules.append((QRegExp("//[^\n]*"), singleLineCommentFormat))

        multiLineCommentFormat = QTextCharFormat()
        multiLineCommentFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        multiLineCommentFormat.setForeground(QColor(Qt.GlobalColor.red if is_night_mode else Qt.GlobalColor.darkRed))
        self.multiLineCommentFormat = multiLineCommentFormat

        numberFormat = QTextCharFormat()
        numberFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        numberFormat.setForeground(QColor(Qt.GlobalColor.yellow if is_night_mode else Qt.GlobalColor.darkYellow))
        self.highlightingRules.append((QRegExp("\\b\\d+\\b"), numberFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(QColor(Qt.GlobalColor.green if is_night_mode else Qt.GlobalColor.darkGreen))
        quotationFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        self.highlightingRules.append((QRegExp('".*"'), quotationFormat))
        self.highlightingRules.append((QRegExp("'.*'"), quotationFormat))
        self.highlightingRules.append((QRegExp("`.*`"), quotationFormat))

        functionFormat = QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        functionFormat.setForeground(QColor(Qt.GlobalColor.lightGray if is_night_mode else Qt.GlobalColor.gray))
        self.highlightingRules.append(
            (QRegExp("\\b[A-Za-z0-9_]+(?=\\()"), functionFormat)
        )

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
                commentLength = (
                    endIndex - startIndex + self.commentEndExpression.matchedLength()
                )

            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(
                text, startIndex + commentLength
            )


class HTMLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(HTMLHighlighter, self).__init__(parent)

        is_night_mode = mw.pm.night_mode()

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor(Qt.GlobalColor.cyan if is_night_mode else Qt.GlobalColor.blue))
        keywordFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        keywordFormat.setFontWeight(QFont.Weight.Bold)

        self.highlightingRules = []

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        singleLineCommentFormat.setForeground(QColor(Qt.GlobalColor.red if is_night_mode else Qt.GlobalColor.darkRed))
        self.highlightingRules.append((QRegExp("\<.*\>"), singleLineCommentFormat))

        keywordPatterns = [
            "\\bstyle\\b",
            "\\bmeta\\b",
            "\\bhead\\b",
            "\\bheader\\b",
            "\\bdiv\\b",
            "\\bspan\\b",
            "\\bem\\b",
            "\\bb\\b",
            "\\bi\\b",
            "\\bu\\b",
            "\\bblockquote\\b",
            "\\btextarea\\b",
            "\\btable\\b",
            "\\bh1\\b",
            "\\bh2\\b",
            "\\bh3\\b",
            "\\bh4\\b",
            "\\bh5\\b",
            "\\bh6\\b",
            "\\bhr\\b",
            "\\bpre\\b",
            "\\bcode\\b",
            "\\bbutton\\b",
        ]

        self.highlightingRules.extend(
            [(QRegExp(pattern), keywordFormat) for pattern in keywordPatterns]
        )

        multiLineCommentFormat = QTextCharFormat()
        multiLineCommentFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        multiLineCommentFormat.setForeground(QColor(Qt.GlobalColor.red if is_night_mode else Qt.GlobalColor.darkRed))
        self.multiLineCommentFormat = multiLineCommentFormat

        numberFormat = QTextCharFormat()
        numberFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        numberFormat.setForeground(QColor(Qt.GlobalColor.yellow if is_night_mode else Qt.GlobalColor.darkYellow))
        self.highlightingRules.append((QRegExp("\\b\\d+\\b"), numberFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(QColor(Qt.GlobalColor.green if is_night_mode else Qt.GlobalColor.darkGreen))
        quotationFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        self.highlightingRules.append((QRegExp('".*"'), quotationFormat))
        self.highlightingRules.append((QRegExp("'.*'"), quotationFormat))
        self.highlightingRules.append((QRegExp("`.*`"), quotationFormat))

        selfTagFormat = QTextCharFormat()
        # selfTagFormat.setFontWeight(QFont.Weight.Bold)
        selfTagFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        selfTagFormat.setForeground(QColor(Qt.GlobalColor.lightGray if is_night_mode else Qt.GlobalColor.gray))
        self.highlightingRules.append((QRegExp("\{\{[^<]+\}\}"), selfTagFormat))

        tagFormat = QTextCharFormat()
        # tagFormat.setFontWeight(QFont.Weight.Bold)
        tagFormat.setFontStyleHint(QFont.StyleHint.Monospace)
        tagFormat.setForeground(QColor(Qt.GlobalColor.magenta if is_night_mode else Qt.GlobalColor.darkMagenta))
        tagRegex = QRegExp("\{\{%.+\}\}")
        tagRegex.setMinimal(True)
        self.highlightingRules.append((tagRegex, tagFormat))

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")



    def highlightBlock(self, text): #chatgpt
        # --- Handle normal syntax rules ---
        for pattern, format in self.highlightingRules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                index = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(index, length, format)
    
        self.setCurrentBlockState(0)
    
        # --- Handle multi-line comments ---
        startIndex = 0
        if self.previousBlockState() != 1:
            start_match = self.commentStartExpression.match(text)
            startIndex = start_match.capturedStart() if start_match.hasMatch() else -1
    
        while startIndex >= 0:
            end_match = self.commentEndExpression.match(text, startIndex)
            if end_match.hasMatch():
                endIndex = end_match.capturedStart()
                commentLength = endIndex - startIndex + end_match.capturedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
    
            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
    
            # Look for next comment start
            next_match = self.commentStartExpression.match(text, startIndex + commentLength)
            startIndex = next_match.capturedStart() if next_match.hasMatch() else -1