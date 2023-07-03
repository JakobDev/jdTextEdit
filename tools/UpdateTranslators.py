#!/usr/bin/env python
import subprocess
import pathlib
import json


WEBLATE_COMMITER = "Codeberg Translate"


AUTHOTS_BLACKLIST = (
    "JakobDev",
    "Weblate"
)


def get_git_authors(path: pathlib.Path) -> list[str]:
    result = subprocess.run(["git", "--no-pager", "log", f"--committer={WEBLATE_COMMITER}", "--pretty=%an", str(path)], capture_output=True, check=True)
    authors: list[str] = []
    for i in result.stdout.decode("utf-8").splitlines():
        if i not in AUTHOTS_BLACKLIST:
            authors.append(i)
    return authors


def parse_translation_directory(path: pathlib.Path, prefix: str, suffix: str, translator_dict: dict[str, list[str]]) -> None:
    for file in path.iterdir():
        if file.suffix != suffix:
            continue

        lang = file.stem.removeprefix(prefix)

        if lang in ("en", "de"):
            continue

        if lang in translator_dict:
            translator_dict[lang] += get_git_authors(file)
        else:
            translator_dict[lang] = get_git_authors(file)


def main() -> None:
    root_dir = pathlib.Path(__file__).parent.parent

    translator_dict: dict[str, list[str]] = {}
    parse_translation_directory(root_dir / "jdTextEdit" / "plugins" / "Pluginmanager" / "translations", "", ".json", translator_dict)
    parse_translation_directory(root_dir / "jdTextEdit" / "plugins" / "SpellChecker" / "translations", "", ".json", translator_dict)
    parse_translation_directory(root_dir / "jdTextEdit" / "translations", "jdTextEdit_", ".ts", translator_dict)
    parse_translation_directory(root_dir / "deploy" / "translations", "", ".po", translator_dict)

    write_dict = {}
    for lang, translators in translator_dict.items():
        write_dict[lang] = sorted(list(set(translators)))

    with open(root_dir / "jdTextEdit" / "data" / "translators.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(write_dict, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    main()
