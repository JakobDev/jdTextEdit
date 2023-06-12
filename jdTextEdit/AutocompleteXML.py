from PyQt6.Qsci import QsciAPIs, QsciLexer
from lxml import etree


class AutocompleteXML(QsciAPIs):
    def __init__(self, lexer: QsciLexer, path: str) -> None:
        super().__init__(lexer)

        root = etree.parse(path).getroot()
        opts = self._getEnvironmentOptions(root)

        for i in root.find("AutoComplete").findall("KeyWord"):
            currentComplete = i.get("name")
            if i.get("func") == "yes":
                currentComplete += opts["startFunc"]
                overloadTag = i.find("Overload")
                currentComplete += opts["paramSeparator"].join([i.get("name") for i in overloadTag.findall("Param")])
                currentComplete += opts["stopFunc"]
                currentComplete += " " + overloadTag.get("descr", "")
            self.add(currentComplete)

        self.prepare()

    def _getEnvironmentOptions(self, root: etree.Element) -> dict[str, str]:
        environmentTag = root.find("Environment")
        if environmentTag is None:
            environmentTag = root.find("AutoComplete").find("Environment")
        if environmentTag is None:
            return {"startFunc": "(", "stopFunc": ")", "paramSeparator": ","}
        return {
            "startFunc": environmentTag.get("startFunc"),
            "stopFunc": environmentTag.get("stopFunc"),
            "paramSeparator": environmentTag.get("paramSeparator")
        }
