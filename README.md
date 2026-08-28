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
  _index.md               front page; a body here overrides the tagline
  games.md                /games/, built from the {{< game >}} shortcode
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
  _shortcodes/game.html   one entry on the games page
assets/css/main.css       all the styling
static/
  uploads/                media from the archive (~433 MB)
  favicon.svg  CNAME
tools/
  import_bar.py           the one-time .bar -> content/ conversion (see below)
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

## The tagline

`description` in `hugo.toml` is the one place it lives: it's the line under the
site name on the front page, the `<meta name="description">`, and the OpenGraph
description. Writing a body into `content/_index.md` replaces the visible line
with that instead, leaving the meta tags alone.

## Adding a game

`content/games.md` is a list of `game` shortcodes, newest first:

```
{{< game name="Bird Bonkers" date="December 2025"
         url="https://rosskarchner.itch.io/bird-bonkers"
         video="/uploads/2025/clip.mp4" poster="/uploads/2025/still.jpg" >}}
The blurb, in Markdown.
{{< /game >}}
```

Pass `video` (optionally with `poster`) or `image`, not both.

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

## How the posts got here

`tools/import_bar.py` did the one-time conversion: it read
`reference/feed.json`, wrote a Markdown file per post, and copied the archive's
media into `static/uploads/`. It's kept as a record of how the import was done,
not as a tool to run again — `content/` is the source of truth now, and
re-running it would overwrite `content/posts/` and discard any edits since.

## Media that still lives on micro.blog

The archive did not include everything the posts embed. These are still hotlinked
and will break if the micro.blog account goes away:

- 6 screencasts served as HLS from `cdn.uploads.micro.mov`, plus their poster
  frames on `cdn.uploads.micro.blog`

The ~143 book covers that used to hotlink `cdn.micro.blog` (the "Finished
reading" posts) are now local, under `static/uploads/books/<isbn>.jpg`.

Everything else is committed under `static/uploads/`, ~207 MB. No file is over
GitHub's 50 MB warning threshold; the largest is 16 MB.

## The GIF originals

The archive's twelve screen-capture GIFs came to 218 MB — half the repository.
They're now h264 instead (18 MB, same frame counts), and the posts that showed
them embed the `.mp4` alongside each one. Four tiny sprite GIFs, all under
5 KB, were left alone.

The Robo Rampage screencast got the same treatment: it was a 53 MB 1080p
capture at 5.3 Mbps, and is now 720p at 16 MB. The page never renders it wider
than ~670 px, so the extra resolution bought nothing.

The originals are **not in this repository or its history**. They live in a
private S3 bucket, at the same paths they had on the site (the screencast with
an `-original-1080p` suffix, since its path is still in use):

```
s3://ross-karchner-com-media-archive/uploads/2023/roguelike.gif
aws s3 ls s3://ross-karchner-com-media-archive/uploads/ --recursive
```

Nothing on the site links to them, so the bucket is a cold archive — versioned
and encrypted, with public access blocked. To restore one, `aws s3 cp` it back
into `static/uploads/`.

To convert another GIF:

```sh
ffmpeg -i in.gif -movflags +faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -crf 23 -preset slow -an out.mp4
```

## Deployment

Pushing to `main` runs `.github/workflows/deploy.yml`: it installs the pinned
Hugo version, builds, and publishes `public/` with `actions/deploy-pages`. The
Pages source is set to "GitHub Actions" in the repository settings.

DNS lives in Route 53 (`karchner.com` hosted zone): `ross.karchner.com` is a
`CNAME` to `rosskarchner.github.io`, and the parent domain is verified for
GitHub Pages by the `_github-pages-challenge-rosskarchner` TXT record.
