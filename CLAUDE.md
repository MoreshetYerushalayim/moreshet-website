# moreshetyerushalayim.com — static rebuild of the school's Wix site

Owner: Victor Dweck (marketing director). The site must stay visually identical to the old Wix site.

## Layout
- `site/` — what Cloudflare Pages serves (output directory).
  - `<page>.html` desktop layout, `_m/<page>.html` phone layout of the same page.
    `functions/_middleware.js` serves the `_m/` version to phones at the SAME address (like Wix).
    **Every content edit must be made in BOTH files.**
  - `media/` images, `assets/` Wix CSS + fonts + `site.js`/`site.css` (our runtime: pop-ups,
    phone menu, slideshow, galleries, entrance animations).
  - `_files/ugd/` magazine PDFs at their original Wix URLs. PDFs over 25 MB are NOT here: they are
    assets of the GitHub release `files` and are served by `functions/_middleware.js` (BIG_PDFS map).
  - `_redirects` old Wix redirects (301), `_headers` PDF download names, `embeds/donate.html` PayPal button.
- `tools/` — the scripts that built the site from captures of the live Wix site (reference only).

## Deliberate changes from the Wix original
- Phones: Team tiles 2 per row and Alumni logos 3 per row (`site/assets/mobile-compact.css`, phone pages only).
- Fixed page titles: Code of Conduct, Visa Information, Ovadia Buddy Sutton, Saul E. Ashkenazi
  (`/copy-of-ovaida-buddy-sutton` is the Saul E. Ashkenazi page, not a duplicate — keep it).

## Editing
- Pages are Wix's rendered HTML. Find content by its visible text and edit in place; keep Wix class
  names/ids. To add a team tile or magazine card, duplicate an existing one in both layouts.
- Team bios are `<template class="site-popup" data-popup-group="popup" data-popup-index="N">` at the
  end of `team.html` / `_m/team.html`; index N matches the Nth "About" button on the page.
- New images go in `site/media/`; new PDFs in `site/_files/ugd/` (or the `files` release if > 25 MB,
  plus a BIG_PDFS entry).
- Commit to `main`; Cloudflare Pages deploys automatically in about a minute.

## Open items
- Instagram feed on /media is a frozen snapshot until the school's Instagram is connected (live feed + Load more).
- Campus map uses Google's keyless embed (pin + place card); exact Wix look needs a Maps API key.
