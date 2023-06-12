from PyQt6.QtWidgets import QDialog, QLabel, QCheckBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.Types import ExportDataType
from PyQt6.QtCore import QCoreApplication
from typing import List
import platform
import datetime
import pathlib
import zipfile
import json
import os


class ExportDataWindow(QDialog):
    def __init__(self, env):
        super().__init__()
        self._env = env

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("ExportDataWindow", "Choose which data you want to export")))

        self._checkboxList = []
        for i in env.exportDataList:
            checkBox = QCheckBox(i["name"])
            checkBox.stateChanged.connect(self._updateOkButtonEnabled)
            mainLayout.addWidget(checkBox)
            self._checkboxList.append(checkBox)

        self._okButton = QPushButton(QCoreApplication.translate("ExportDataWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("ExportDataWindow", "Cancel"))

        self._okButton.clicked.connect(self._okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(self._okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(self._okButton)
        mainLayout.addLayout(buttonLayout)

        self._updateOkButtonEnabled()

        self.setWindowTitle(QCoreApplication.translate("ExportDataWindow", "Export data"))
        self.setLayout(mainLayout)

    def _createArchive(self, outPath: str, dataList: List[ExportDataType]) -> None:
        zf = zipfile.ZipFile(outPath, "w")

        for i in dataList:
            for currentPath in i["path"]:
                fullPath = os.path.join(self._env.dataDir, currentPath)
                if os.path.isdir(fullPath):
                    for p in pathlib.Path(fullPath).rglob("*"):
                        zf.write(p, arcname=str(p).removeprefix(self._env.dataDir))
                elif os.path.isfile(fullPath):
                    zf.write(fullPath, arcname=currentPath)

        exportData = {
            "dateTime": datetime.datetime.now().isoformat(),
            "platform": platform.system(),
            "version": self._env.version,
            "dataList": [i["id"] for i in dataList]
        }
        zf.writestr("jdTextEditExportData.json", json.dumps(exportData, ensure_ascii=False, indent=4))

        zf.close()

    def _updateOkButtonEnabled(self):
        for i in self._checkboxList:
            if i.isChecked():
                self._okButton.setEnabled(True)
                return
        self._okButton.setEnabled(False)

    def _okButtonClicked(self):
        zipFilterText = QCoreApplication.translate("ExportDataWindow", "Zip Files")
        allFilterText = QCoreApplication.translate("ExportDataWindow", "All Files")

        path = QFileDialog.getSaveFileName(self, filter=f"{zipFilterText} (*.zip);;{allFilterText} (*)")[0]

        if path == "":
            return

        exportList = []
        for count, i in enumerate(self._checkboxList):
            if i.isChecked():
                exportList.append(self._env.exportDataList[count])

        self._createArchive(path, exportList)

        QMessageBox.information(self, QCoreApplication.translate("ExportDataWindow", "Export complete"), QCoreApplication.translate("ExportDataWindow", "You data were successfully exported"))

        self.close()
