#!/usr/bin/env python
import subprocess
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of writing to the file")
    args = parser.parse_args()

    root_dir = pathlib.Path(__file__).parent.parent

    translator_dict: dict[str, list[str]] = {}
    parse_translation_directory(root_dir / "jdTextEdit" / "plugins" / "Pluginmanager" / "translations", "", ".json", translator_dict)
    parse_translation_directory(root_dir / "jdTextEdit" / "plugins" / "SpellChecker" / "translations", "", ".json", translator_dict)
    parse_translation_directory(root_dir / "jdTextEdit" / "translations", "jdTextEdit_", ".ts", translator_dict)
    parse_translation_directory(root_dir / "deploy" / "translations", "", ".po", translator_dict)

    write_dict = {}
    for lang in sorted(translator_dict.keys()):
        write_dict[lang] = sorted(list(set(translator_dict[lang])))

    if args.stdout:
        print(json.dumps(write_dict, ensure_ascii=False, indent=4))
    else:
        with open(root_dir / "jdTextEdit" / "data" / "translators.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(write_dict, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    main()
