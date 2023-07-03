#!/usr/bin/env python
from pathlib import Path
import subprocess
import argparse
import platform
import shutil
import gzip
import sys
import os


def make_directory(dir_path: Path) -> None:
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass


def install_file(source: Path, dest: Path) -> None:
    if not os.path.isdir(dest.parent):
        os.makedirs(dest.parent)
    shutil.copyfile(source, dest)


def gzip_file(in_path: Path, out_path: Path) -> None:
    if not os.path.isdir(out_path.parent):
        os.makedirs(out_path.parent)
    with open(in_path, "rb") as f:
        data = f.read()
    with gzip.open(out_path, "wb") as f:
        f.write(data)


def install_locales(current_dir: Path, prefix: Path) -> None:
    for i in (current_dir / "jdTextEdit" / "translations").iterdir():
        if i.suffix != ".ts":
            continue
        lang = i.stem.removeprefix("jdTextEdit_")
        try:
            os.makedirs(prefix / "share" / "locale" / lang / "LC_MESSAGES")
        except Exception:
            pass
        subprocess.check_call(["lrelease", str(i), "-qm", str(prefix / "share" / "locale" / lang / "LC_MESSAGES" / "jdtextedit.qm")])


def install_unix_data_files(current_dir: Path, args: argparse.Namespace) -> None:
    install_file(current_dir / "jdTextEdit" / "Logo.svg", Path(args.prefix) / "share" / "icons" / "hicolor" / "scalable" / "apps" / "page.codeberg.JakobDev.jdTextEdit.svg")
    install_file(current_dir / "deploy" / "page.codeberg.JakobDev.jdTextEdit.service", Path(args.prefix) / "share" / "dbus-1" / "services" / "page.codeberg.JakobDev.jdTextEdit.service")

    make_directory(Path(args.prefix) / "share" / "applications")
    make_directory(Path(args.prefix) / "share" / "metainfo")

    subprocess.run(["msgfmt", "--desktop", "--template", os.path.join(current_dir, "deploy", "page.codeberg.JakobDev.jdTextEdit.desktop"), "-d", os.path.join(current_dir, "deploy", "translations"), "-o", os.path.join(args.prefix, "share", "applications", "page.codeberg.JakobDev.jdTextEdit.desktop")], check=True)
    subprocess.run(["msgfmt", "--xml", "--template", os.path.join(current_dir, "deploy", "page.codeberg.JakobDev.jdTextEdit.metainfo.xml"), "-d", os.path.join(current_dir, "deploy", "translations"), "-o", os.path.join(args.prefix, "share", "metainfo", "page.codeberg.JakobDev.jdTextEdit.metainfo.xml")], check=True)

    if args.install_manpage:
        subprocess.check_call(["make", "man"], cwd=str(current_dir / "doc"))
        gzip_file(current_dir / "doc" / "build" / "man" / "jdtextedit.1", Path(args.prefix) / "share" / "man" / "man1" / "jdtextedit.1.gz")

    if args.install_html_doc:
        subprocess.check_call(["make", "html"], cwd=str(current_dir / "doc"))
        shutil.copytree(current_dir / "doc" / "build" / "html", Path(args.prefix) / "share" / "doc" / "jdTextEdit")

    if args.install_locales:
        install_locales(current_dir, Path(args.prefix))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--yes", help="Say yes to the install question", action="store_true")
    parser.add_argument("--no-deps", help="Don't install dependencies", action="store_true")
    parser.add_argument("--prefix", help="The prefix", default="/usr")
    parser.add_argument("--distribution-file", help="The distribution.json")
    if platform.system() == "Linux":
        parser.add_argument("--install-manpage", help="Installs the manpage (needs sphinx)", action="store_true")
        parser.add_argument("--install-html-doc", help="Installs the html documentation into share/doc/jdTextEdit (needs sphinx and sphinx-rtd-theme)", action="store_true")
        parser.add_argument("--install-locales", help="Installs the locales into share/locale (needs lrelease)", action="store_true")
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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "--ignore-installed", "--no-build-isolation", "--prefix", args.prefix, str(current_dir), "-r", str(current_dir / "requirements.txt")])

    subprocess.call([sys.executable, "-m", "pip", "install", "-U", "--no-deps", "--ignore-installed", "--no-build-isolation", "--prefix", args.prefix, str(current_dir)])

    if platform.system() == "Linux":
        install_unix_data_files(current_dir, args)

    if args.distribution_file:
        install_file(Path(args.distribution_file), Path(args.prefix) / "lib" / "python{}.{}".format(*sys.version_info) / "site-packages" / "jdTextEdit" / "distribution.json")


if __name__ == "__main__":
    main()
