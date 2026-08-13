# ross.karchner.com

A [Hugo](https://gohugo.io) blog, built by GitHub Actions and served by GitHub
Pages at <https://ross.karchner.com>.

The posts came from a `.bar`
([blog archive format](https://indieweb.org/blog_archive_format)) export of
`rossk.micro.blog` — 417 posts from October 2023 onward, plus the media they
reference.

## Layout

```
hugo.toml                 site config: permalinks, feeds, footer links
content/
  _index.md               the blurb at the top of the front page
  posts/                  one Markdown file per post, YYYY-MM-DD-slug.md
  tags/_index.md          blurb on the tag index
layouts/                  the theme (no external theme, no submodules)
  baseof.html             page shell
  home.html               the front page: paginated stream
  home.hfeed.html         /all.html — every post, full text, one h-feed
  home.jsonfeed.json      /feed.json — JSON Feed
  home.rss.xml            /index.xml — RSS, full text
  section.html            /posts/ — dated archive index
  taxonomy.html term.html /tags/ and /tags/<tag>/
  single.html 404.html
  _partials/              post.html and the small head/footer pieces
assets/css/main.css       all the styling
static/
  uploads/                media from the archive (~433 MB)
  favicon.svg  CNAME
tools/
  import_bar.py           .bar archive -> content/posts/ + static/uploads/
  export_bar.py           built site -> a .bar archive
reference/                the extracted .bar this site was seeded from
.github/workflows/deploy.yml
```

## Writing

```sh
hugo new content posts/$(date +%F)-a-new-post.md
```

Delete the `title` line and add `microblog: true` for a short, title-less post —
those render in full in the stream, while titled posts show a summary with a
"Read more" link.

## Previewing

```sh
hugo server -D          # http://localhost:1313
```

## Permalinks

Posts keep the paths they had on micro.blog, e.g.
`/2026/07/18/or-not.html`. That comes from two settings in `hugo.toml`:

```toml
[permalinks.page]
  posts = "/:year/:month/:day/:slug"

[uglyURLs]
  posts = true
```

Don't change either one without leaving redirects behind.

## Feeds and archiving

| URL          | What                                                     |
| ------------ | -------------------------------------------------------- |
| `/index.xml` | RSS, full text, every post                                |
| `/feed.json` | [JSON Feed](https://jsonfeed.org), full text, every post  |
| `/all.html`  | every post in one microformats2 `h-feed`                  |

Those are exactly the three pieces a `.bar` archive needs, so the site can
re-export itself:

```sh
hugo && python3 tools/export_bar.py   # -> ross-karchner.bar
```

## Re-importing the archive

`tools/import_bar.py` is rerunnable — it wipes `content/posts/` and rebuilds it
from `reference/feed.json`, rewriting micro.blog URLs to local ones. Any edits
made to imported posts would be lost, so run it only to redo the import:

```sh
python3 tools/import_bar.py --archive reference
```

## Media that still lives on micro.blog

The archive did not include everything the posts embed. These are still hotlinked
and will break if the micro.blog account goes away:

- ~143 book covers on `cdn.micro.blog` (the "Finished reading" posts)
- 6 screencasts served as HLS from `cdn.uploads.micro.mov`, plus their poster
  frames on `cdn.uploads.micro.blog`

Everything else — 305 files, ~433 MB — is committed under `static/uploads/`.
One of them, `static/uploads/2025/screencast-from-2025-02-22-22-40-54.mp4`
(53 MB), is over GitHub's 50 MB warning threshold but under the 100 MB limit.

## Deployment

Pushing to `main` runs `.github/workflows/deploy.yml`: it installs the pinned
Hugo version, builds, and publishes `public/` with `actions/deploy-pages`. The
Pages source is set to "GitHub Actions" in the repository settings.

DNS lives in Route 53 (`karchner.com` hosted zone): `ross.karchner.com` is a
`CNAME` to `rosskarchner.github.io`, and the parent domain is verified for
GitHub Pages by the `_github-pages-challenge-rosskarchner` TXT record.
