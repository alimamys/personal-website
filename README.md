# Personal website — Dr. Saifeddin Alimamy

A single-page static site (HTML/CSS/JS, no build step). The page tells one story, in this order:

1. Announcement bar and navigation
2. Hero and academic impact strip (citations, h-index, funding, FHEA, ILM)
3. About, then Faculty leadership & teaching
4. Research themes, then Selected research (5 featured papers + 3 latest)
5. From research to practice (the bridge section)
6. Ways we can work together, Featured workshops & executive education
7. Selected training & engagement experience, Selected talks & conference presentations
8. Closing call to action, Contact

All factual content comes from the CV (July 2026). Unverified items are listed as
`TODO` comments in `index.html`; search for `TODO` before adding new claims.

## Preview locally

Run `python3 -m http.server` in this folder and visit http://localhost:8000.

## Contact form: one configuration step

Enquiries currently open the visitor's email app (a `mailto:` fallback, with a
"copy enquiry" option if no email app opens). To receive enquiries directly, with an
on-page "Thank you" confirmation:

1. Create a free form at [Formspree](https://formspree.io) using the address that should
   receive enquiries.
2. Copy the form's endpoint URL (it looks like `https://formspree.io/f/abcdwxyz`).
3. In `index.html`, paste it into the empty `data-endpoint=""` attribute on
   `<form id="contact-form">`.

The endpoint URL is public by design and is not a secret key. If sending ever fails,
the form shows the direct email address and the copy option instead.

## Customize

- **Photo:** add `assets/portrait.jpg` and follow the TODO comment above the hero in
  `index.html` (it switches the hero to a two-column layout).
- **Testimonials:** a styled component is ready but hidden until genuine, attributable
  quotes exist. See the TODO comment in the training experience section.
- **LinkedIn / ORCID:** uncomment the lines in the Contact section and fill in your links.
- **Featured publications:** edit the `<ol class="pubs">` list. Keep each
  `<span class="cites" data-cites="…">` so the weekly update can add citation counts.

## Automatic citation updates

`.github/workflows/update-scholar.yml` runs every Monday (and on demand from the
**Actions** tab → *Update citations from Google Scholar* → *Run workflow*). It runs
`scripts/update_scholar.py`, which refreshes:

- citations, h-index and the "updated" date in the header
- the "Cited by N" badge on each selected publication
- the "Latest publications" list (newest three from Google Scholar, skipping papers
  already featured in Selected research)

Google Scholar often blocks automated requests from GitHub's servers. For reliable
updates, create a free [SerpApi](https://serpapi.com) account and add its API key as a
repository secret named `SERPAPI_KEY` (**Settings → Secrets and variables → Actions**).
If no data can be fetched, the site is left unchanged and the run shows a warning.

Scheduled workflows run only on the repository's default branch.

## Publish with GitHub Pages

Repository **Settings → Pages → Build and deployment → Deploy from a branch**, choose the branch and `/ (root)`.
GitHub rebuilds the site on every push. Live address: https://alimamys.github.io/personal-website/
