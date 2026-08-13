#!/usr/bin/env python3
"""Package the built site as a .bar blog archive.

A .bar (https://indieweb.org/blog_archive_format) is a zip containing

    feed.json    a JSON Feed with the full content of every post
    index.html   the same posts as a microformats2 h-feed
    uploads/     the media the posts reference

Hugo already emits all three, so this just zips them up — which means the
archive that seeded this site can be regenerated from it.

Usage:  hugo && python3 tools/export_bar.py [--out ross-karchner.bar]
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import zipfile


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", default=root / "public", type=pathlib.Path)
    parser.add_argument("--out", default=root / "ross-karchner.bar", type=pathlib.Path)
    args = parser.parse_args()

    feed = args.public / "feed.json"
    if not feed.is_file():
        print(f"{feed} not found — run `hugo` first", file=sys.stderr)
        return 1

    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as bar:
        bar.write(feed, "feed.json")
        # /all.html is the h-feed of every post in full; the front page only
        # carries the most recent pageful.
        bar.write(args.public / "all.html", "index.html")
        for path in sorted((args.public / "uploads").rglob("*")):
            if path.is_file():
                bar.write(path, str(path.relative_to(args.public)))

    size = args.out.stat().st_size / 1_000_000
    print(f"wrote {args.out.name} ({size:.0f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
