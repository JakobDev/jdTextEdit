#!/usr/bin/env python
from pathlib import Path
import subprocess
import shutil
import sys
import os


def updateDirectory(translationDir: Path) -> None:
    for i in translationDir.iterdir():
        if i.suffix == ".ts":
            subprocess.run(["pylupdate6", "jdTextEdit", "--ts", os.path.join(translationDir, i.name), "--no-obsolete"], cwd=Path(__file__).parent)


def main():
    if not shutil.which("pylupdate6"):
        print("pylupdate6 was not found")
        sys.exit(1)

    updateDirectory((Path(__file__).parent / "jdTextEdit" / "i18n"))


if __name__ == "__main__":
    main()
