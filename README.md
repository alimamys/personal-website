# Personal website — Dr. Saifeddin Alimamy

A single-page static site (HTML/CSS/JS, no build step) with:

- Profile, education and research interests
- Selected publications (links to DOIs and Google Scholar)
- "Work with me" section: research collaboration, workshops & talks, trainings, consultations
- Contact form that pre-selects the inquiry type

## Preview locally

Open `index.html` in a browser, or run `python3 -m http.server` and visit http://localhost:8000.

## Customize

- **Photo:** add `assets/portrait.jpg` and replace the `SA` placeholder inside `.portrait` in `index.html`.
- **LinkedIn / ORCID:** uncomment the lines in the Contact section and fill in your links.
- **Publications:** edit the `<ol class="pubs">` list.
- **Contact form:** by default it opens the visitor's email app with a pre-filled message.
  To receive submissions directly, create a free form at [Formspree](https://formspree.io) and set
  `FORM_ENDPOINT` at the top of the form section in `script.js`.

## Automatic citation updates

`.github/workflows/update-scholar.yml` runs every Monday (and on demand from the
**Actions** tab → *Update citations from Google Scholar* → *Run workflow*). It runs
`scripts/update_scholar.py`, which refreshes:

- citations, h-index and the "updated" date in the header
- the "Cited by N" badge on each selected publication
- the "Latest publications" list (newest five from Google Scholar)

Google Scholar often blocks automated requests from GitHub's servers. For reliable
updates, create a free [SerpApi](https://serpapi.com) account and add its API key as a
repository secret named `SERPAPI_KEY` (**Settings → Secrets and variables → Actions**).
If no data can be fetched, the site is left unchanged and the run shows a warning.

Scheduled workflows run only on the repository's default branch.

## Publish with GitHub Pages

Repository **Settings → Pages → Build and deployment → Deploy from a branch**, choose the branch and `/ (root)`.
GitHub rebuilds the site on every push. Live address: https://alimamys.github.io/personal-website/
