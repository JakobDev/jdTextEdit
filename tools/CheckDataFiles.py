#!/usr/bin/env python
import subprocess
import pathlib
import sys


def check_file(tool: str, path: pathlib.Path, text: str) -> None:
    result = subprocess.run([sys.executable, str(pathlib.Path(__file__).parent / tool), "--stdout"], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error while running {tool}:\n" + result.stderr, file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8", newline="\n") as f:
        content = f.read()

    if result.stdout.strip() != content.strip():
        print(text, file=sys.stderr)
        sys.exit(1)


def main() -> None:
    root_dir = pathlib.Path(__file__).parent.parent

    check_file("UpdateTranslators.py", root_dir / "jdTextEdit" / "data" / "translators.json", "The translators are not up to date. Please run tools/UpdateTranslators.py.")
    check_file("WriteChangelogHtml.py", root_dir / "jdTextEdit" / "data" / "changelog.html", "The changelog is not up to date. Please run tools/WriteChangelogHtml.py.")

    print("All data files are up to date")


if __name__ == "__main__":
    main()