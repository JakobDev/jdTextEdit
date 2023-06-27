#!/usr/bin/env python
import subprocess
import pathlib
import shutil
import sys
import os


def main():
    if not shutil.which("pylupdate6"):
        print("pylupdate6 was not found")
        sys.exit(1)

    for i in (pathlib.Path(__file__).parent.parent / "jdTextEdit" / "translations").iterdir():
        if i.suffix == ".ts":
            subprocess.run(["pylupdate6", "jdTextEdit", "--ts", os.path.join("jdTextEdit", "translations", i.name), "--no-obsolete"], cwd=pathlib.Path(__file__).parent.parent)


if __name__ == "__main__":
    main()
