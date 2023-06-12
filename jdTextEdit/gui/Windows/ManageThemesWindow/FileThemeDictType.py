from typing import TypedDict

FileThemeDict = TypedDict("FileThemeDict", {
    "id": str,
    "name": str,
    "global": dict[str, str],
    "lexer": dict[str, dict[str, str]]
})
