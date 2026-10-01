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

## Publish with GitHub Pages

Repository **Settings → Pages → Build and deployment → Deploy from a branch**, choose the branch and `/ (root)`.
