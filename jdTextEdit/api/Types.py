from typing import TypedDict


class ExportDataType(TypedDict):
    id: str
    name: str
    path: list[str]


class DistributionSettingsType(TypedDict,  total=False):
    enableUpdater: bool
    dataDirectory: str
    aboutMessage: str
    templateDirectories: list[str]
    enableTranslationWarning: bool


class EncodingDetectFunctionResult(TypedDict):
    encoding: str
    language: str
    confidence: float
