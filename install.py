#!/usr/bin/env python
from pathlib import Path
import subprocess
import argparse
import platform
import shutil
import sys
import os


def install_file(source: Path, dest: Path):
    if not os.path.isdir(dest.parent):
        os.makedirs(dest.parent)
    shutil.copyfile(source, dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--yes", help="Say yes to the install question", action="store_true")
    parser.add_argument("--no-deps", help="Don't install dependencies", action="store_true")
    parser.add_argument("--prefix", help="The prefix", default="/usr")
    parser.add_argument("--distribution-file", help="The distribution.json")
    args = parser.parse_args()

    if not args.yes:
        print("This script will install jdTextEdit on your computer. It is recommend to use a Package or Flatpak to install jdTextEdit instead of this script.")
        print(f"The current install location is {args.prefix}. Pass --prefix to change it.")
        while True:
            answer = input("Continue [Y/N]: ").lower()
            if answer == "n":
                sys.exit(0)
            elif answer == "y":
                break

    try:
        subprocess.check_call([sys.executable, "-m", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("pip is not installed for the current python version", file=sys.stderr)
        sys.exit(1)

    current_dir = Path(__file__).parent

    if not args.no_deps:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "--ignore-installed", "--prefix", args.prefix, str(current_dir), "-r", str(current_dir / "requirements.txt")])

    subprocess.call([sys.executable, "-m", "pip", "install", "-U", "--no-deps", "--ignore-installed", "--prefix", args.prefix, str(current_dir)])

    if platform.system() == "Linux":
        install_file(current_dir / "jdTextEdit" / "Logo.svg", Path(args.prefix) / "share" / "icons" / "hicolor" / "scalable" / "apps" / "com.gitlab.JakobDev.jdTextEdit.svg")
        install_file(current_dir / "deploy" / "com.gitlab.JakobDev.jdTextEdit.desktop", Path(args.prefix) / "share" / "applications" / "com.gitlab.JakobDev.jdTextEdit.desktop")
        install_file(current_dir / "deploy" / "com.gitlab.JakobDev.jdTextEdit.metainfo.xml", Path(args.prefix) / "share" / "metainfo" / "com.gitlab.JakobDev.jdTextEdit.metainfo.xml")

    if args.distribution_file:
        install_file(Path(args.distribution_file), Path(args.prefix) / "lib" / "python{}.{}".format(*sys.version_info) / "site-packages" / "jdTextEdit" / "distribution.json")


if __name__ == "__main__":
    main()
