from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDockWidget, QComboBox

class DockWidget(QDockWidget):
    def __init__(self, env):
        super().__init__()
        self.env = env
        self.enabled = False
        self.content = DockWidgetContent(env)
        self.setWidget(self.content)

    def closeEvent(self,event):
        self.enabled = False
        self.env.mainWindow.toggleSidebarAction.setChecked(False)
        event.accept()

class DockWidgetContent(QWidget):
    def __init__(self, env):
        super().__init__()
        self.env = env
        self.widgetChooser = QComboBox()
        for i in env.dockWidgtes:
            self.widgetChooser.addItem(i[1])
        layout = QVBoxLayout()
        layout.addWidget(self.widgetChooser)
        layout.addWidget(env.dockWidgtes[0][0])
        self.widgetChooser.currentIndexChanged.connect(self.widgetChanged)
        self.setLayout(layout)

    def widgetChanged(self, index):
        self.layout().itemAt(1).widget().setParent(None)
        self.layout().addWidget(self.env.dockWidgtes[index][0])

    def getSelectedWidget(self):
        index = self.widgetChooser.currentIndex()
        return self.env.dockWidgtes[index][2]

    def setCurrentWidget(self, widget):
        for count, i in enumerate(self.env.dockWidgtes):
            if i[2] == widget:
                self.widgetChooser.setCurrentIndex(count)
