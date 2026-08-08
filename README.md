# ross.karchner.com

A small "linktree"-style landing page, served by GitHub Pages at
<https://ross.karchner.com>.

## Layout

```
site/                     everything published to the web
  index.html              the page
  style.css               styling (light + dark)
  favicon.svg
  CNAME                   custom domain
.github/workflows/deploy.yml   publishes site/ on every push to main
```

No build step and no dependencies — `site/` is uploaded as-is.

## Editing the links

The links live in the `<ul class="links">` block in `site/index.html`. Each one
is a list item carrying its own brand colour via the `--accent` custom property,
which drives the icon fill plus the hover border, focus ring, and arrow.

Brand glyphs are inline SVG paths from [Simple Icons](https://simpleicons.org)
(CC0), embedded so the page makes no external requests.

## Previewing locally

```sh
python3 -m http.server -d site 8000   # then open http://localhost:8000
```

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which uploads `site/`
and deploys it with `actions/deploy-pages`. The Pages source is set to "GitHub
Actions" in the repository settings.

DNS lives in Route 53 (`karchner.com` hosted zone): `ross.karchner.com` is a
`CNAME` to `rosskarchner.github.io`, and the parent domain is verified for
GitHub Pages by the `_github-pages-challenge-rosskarchner` TXT record.
