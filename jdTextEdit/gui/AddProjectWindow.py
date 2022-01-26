from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox, QGridLayout, QHBoxLayout, QVBoxLayout
from jdTextEdit.core.Project import Project
import os


class AddProjectWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self._env = env

        self._nameEdit = QLineEdit()
        self._pathEdit = QLineEdit()
        browseButton = QPushButton(env.translate("button.browse"))
        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))

        browseButton.clicked.connect(self._browseButtonClicked)
        okButton.clicked.connect(self._ok_button_clicked)
        cancelButton.clicked.connect(self.close)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("addProjectWindow.label.name")), 0, 0)
        gridLayout.addWidget(self._nameEdit, 0, 1, 1, 2)
        gridLayout.addWidget(QLabel(env.translate("addProjectWindow.label.path")), 1, 0)
        gridLayout.addWidget(self._pathEdit, 1, 1)
        gridLayout.addWidget(browseButton, 1, 2)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def _browseButtonClicked(self):
        path = QFileDialog.getExistingDirectory(self, None, self._pathEdit.text())
        if path:
            self._pathEdit.setText(path)

    def _generateProjectId(self, name: str) -> str:
        if name not in self._env.projects:
            return name
        count = 0
        while True:
            if f"{name}_{count}" not in self._env.projects:
                return f"{name}_{count}"
            count += 1

    def _ok_button_clicked(self):
        if len(self._nameEdit.text()) == 0:
            QMessageBox.critical(self, self._env.translate("addProjectWindow.noName.title"), self._env.translate("addProjectWindow.noName.text"))
            return

        if not os.path.exists(self._pathEdit.text()):
            QMessageBox.critical(self, self._env.translate("addProjectWindow.invalidPath.title"), self._env.translate("addProjectWindow.invalidPath.text"))
            return

        project_id = self._generateProjectId(self._nameEdit.text())
        p = Project(self._env, project_id, self._nameEdit.text(), self._pathEdit.text())
        self._env.pluginAPI.addProject(p)

        self.close()
