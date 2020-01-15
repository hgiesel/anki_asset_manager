from aqt.qt import QComboBox

class SMConfigModelchooser(QComboBox):
    def __init__(self, mw):
        super().__init__(parent=mw)

    def setupUi(self, modelNames, updateFunc):
        self.addItems([name for name in modelNames])
        self.currentIndexChanged.connect(updateFunc)
