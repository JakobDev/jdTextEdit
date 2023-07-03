#!/usr/bin/env python
import pathlib
import sys


try:
    import appstream_python
except ModuleNotFoundError:
    print("appstream-python was not found. Install it with pip.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    root_dir = pathlib.Path(__file__).parent.parent

    component = appstream_python.AppstreamComponent()
    component.load_file(root_dir / "deploy" / "page.codeberg.JakobDev.jdTextEdit.metainfo.xml")

    html_text = ""
    for release in component.releases:
        html_text += f"<b>{release.version}</b><br>\n"
        description = release.description.to_plain_text().replace("\n", "<br>\n")
        html_text += f"{description}<br>\n<br>\n"
    html_text = html_text.removesuffix("<br>\n<br>\n")

    with open(root_dir / "jdTextEdit" / "data" / "changelog.html", "w", encoding="utf-8", newline="\n") as f:
        f.write(html_text)


if __name__ == "__main__":
    main()