#!/usr/bin/env python3
"""Import a blog archive (.bar) export into Hugo content files.

A .bar archive (https://indieweb.org/blog_archive_format) is a zip containing

    feed.json    a JSON Feed with the full content of every post
    index.html   the same posts as a microformats2 h-feed
    uploads/     the media the posts reference

This reads the extracted archive's feed.json and writes one Markdown file per
item into content/posts/, preserving the original permalink path so links into
the old micro.blog site keep working.

Usage:  python3 tools/import_bar.py [--archive reference] [--out content/posts]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

# Hosts that served this blog; their /uploads/ paths are local files now.
SELF_HOSTS = ("https://rossk.micro.blog", "http://rossk.micro.blog")

# "2026/07/19/or-not.html" -> ("2026", "07", "19", "or-not")
PERMALINK_RE = re.compile(r"/(\d{4})/(\d{2})/(\d{2})/([^/]+)\.html$")


def yaml_str(value: str) -> str:
    """Quote a scalar for YAML front matter."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def rewrite_links(text: str) -> str:
    """Point media and permalinks at this site instead of micro.blog."""
    for host in SELF_HOSTS:
        # Uploads came with the archive, so they are served from /uploads/.
        text = text.replace(f"{host}/uploads/", "/uploads/")
        # Old post permalinks keep their path on the new site.
        text = re.sub(rf"{re.escape(host)}(/\d{{4}}/\d{{2}}/\d{{2}}/)", r"\1", text)
    # The archive's own relative references, e.g. src="uploads/2024/x.png"
    # and ](uploads/2024/x.png), are relative to the archive root.
    text = re.sub(r'((?:src|href|poster)=")uploads/', r"\1/uploads/", text)
    text = re.sub(r"(\]\()uploads/", r"\1/uploads/", text)
    return text


def parse_item(item: dict) -> dict | None:
    """Turn one JSON Feed item into the fields a Hugo page needs."""
    url = item.get("url") or item.get("id", "")
    match = PERMALINK_RE.search(url)
    if not match:
        print(f"skipping item with unrecognized url: {url!r}", file=sys.stderr)
        return None
    year, month, day, slug = match.groups()

    # content_text is the post's original Markdown (with some inline HTML);
    # content_html is that Markdown already rendered. Prefer the source.
    body = item.get("content_text") or item.get("content_html") or ""

    return {
        "year": year,
        "month": month,
        "day": day,
        "slug": slug,
        "title": (item.get("title") or "").strip(),
        "date": item["date_published"],
        "tags": [t for t in item.get("tags", []) if t and t != "Uncategorized"],
        "body": rewrite_links(body).strip(),
        "source_url": url,
    }


def front_matter(post: dict) -> str:
    lines = ["---"]
    if post["title"]:
        lines.append(f"title: {yaml_str(post['title'])}")
    else:
        # A micro post: no title, rendered as a bare entry in the stream.
        lines.append("microblog: true")
    lines.append(f"date: {post['date']}")
    lines.append(f"slug: {yaml_str(post['slug'])}")
    if post["tags"]:
        lines.append("tags:")
        lines.extend(f"  - {yaml_str(t)}" for t in post["tags"])
    lines.append(f"source_url: {yaml_str(post['source_url'])}")
    lines.append("---")
    return "\n".join(lines)


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", default=root / "reference", type=pathlib.Path)
    parser.add_argument("--out", default=root / "content" / "posts", type=pathlib.Path)
    parser.add_argument("--static", default=root / "static", type=pathlib.Path)
    parser.add_argument(
        "--skip-uploads",
        action="store_true",
        help="don't copy the archive's uploads/ into static/",
    )
    args = parser.parse_args()

    feed = json.loads((args.archive / "feed.json").read_text(encoding="utf-8"))
    posts = [p for p in (parse_item(i) for i in feed["items"]) if p]

    if args.out.exists():
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True)

    seen: dict[str, str] = {}
    for post in posts:
        name = f"{post['year']}-{post['month']}-{post['day']}-{post['slug']}.md"
        if name in seen:
            print(f"duplicate permalink: {name}", file=sys.stderr)
            return 1
        seen[name] = post["source_url"]
        (args.out / name).write_text(
            front_matter(post) + "\n\n" + post["body"] + "\n", encoding="utf-8"
        )

    print(f"wrote {len(posts)} posts to {args.out.relative_to(root)}")

    if not args.skip_uploads:
        src, dest = args.archive / "uploads", args.static / "uploads"
        if src.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            count = sum(1 for _ in dest.rglob("*") if _.is_file())
            print(f"copied {count} uploads to {dest.relative_to(root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
