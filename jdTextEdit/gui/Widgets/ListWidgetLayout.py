from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QScrollArea, QHBoxLayout
import uuid


class ListWidgetLayout(QWidget):
    def __init__(self):
        super().__init__()

        self._listWidget = QListWidget()
        self._widgetDict: dict[str, QWidget] = {}
        self._originalWidgetDict: dict[str, QWidget] = {}

        self._listWidget.currentItemChanged.connect(self._changeWidget)

        self._mainLayout = QHBoxLayout()
        self._mainLayout.addWidget(self._listWidget)
        self._mainLayout.addWidget(QWidget())

        self.setLayout(self._mainLayout)

    def _changeWidget(self, item: QListWidgetItem) -> None:
        self._mainLayout.itemAt(1).widget().setParent(None)
        self._mainLayout.addWidget(self._widgetDict[item.data(42)], 3)

    def addWidget(self, title: str, widget: QWidget, scrollable: bool = False):
        currentID = str(uuid.uuid4())

        if scrollable:
            area = QScrollArea()
            area.setWidget(widget)
            self._widgetDict[currentID] = area
        else:
            self._widgetDict[currentID] = widget
        self._originalWidgetDict[title] = widget

        item = QListWidgetItem(title)
        item.setData(42, currentID)
        self._listWidget.addItem(item)

        if len(self._widgetDict) == 1:
            self._mainLayout.itemAt(1).widget().setParent(None)
            self._mainLayout.addWidget(widget, 3)

    def getWidgetList(self) -> list[QWidget]:
        return list(self._originalWidgetDict.values())
