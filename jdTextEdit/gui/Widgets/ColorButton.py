from PyQt6.QtWidgets import QPushButton, QColorDialog
from PyQt6.QtGui import QColor


class ColorButton(QPushButton):
    def __init__(self):
        super().__init__()

        self._currentColor = QColor()
        self.clicked.connect(self._buttonClicked)

    def _buttonClicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setColor(color)

    def setColor(self, color: QColor):
        self.setText(color.name())
        self.setStyleSheet(f"background-color: {color.name()}")
        self._currentColor = color

    def getColor(self) -> QColor:
        return self._currentColor
