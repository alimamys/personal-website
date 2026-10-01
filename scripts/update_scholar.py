"""Refresh citation metrics and publications on the website from Google Scholar.

Run weekly by .github/workflows/update-scholar.yml. It updates, in index.html:
  - elements marked data-scholar="citations" / "h_index" / "i10_index" / "updated"
  - the "Cited by N" badge on each selected publication (data-cites="<title key>")
  - the "Latest publications" list between the scholar:latest markers
and saves the raw data to data/scholar.json.

Data source: if the SERPAPI_KEY environment variable is set, the SerpApi
Google Scholar Author API is used (reliable). Otherwise the public Scholar
profile page is read directly, which Google sometimes blocks for automated
traffic. If no usable data comes back, nothing is changed.
"""

import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SCHOLAR_ID = "yRba7DEAAAAJ"
OWNER_NAME = "Alimamy"  # bolded in author lists
LATEST_COUNT = 5

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
DATA = ROOT / "data" / "scholar.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def to_int(text):
    digits = re.sub(r"\D", "", str(text or ""))
    return int(digits) if digits else 0


def fetch_serpapi(key):
    articles = []
    metrics = {}
    start = 0
    while True:
        res = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_scholar_author",
                "author_id": SCHOLAR_ID,
                "hl": "en",
                "sort": "pubdate",
                "num": 100,
                "start": start,
                "api_key": key,
            },
            timeout=60,
        )
        res.raise_for_status()
        data = res.json()
        if not metrics:
            table = {}
            for row in data.get("cited_by", {}).get("table", []):
                table.update(row)
            metrics = {
                "citations": to_int(table.get("citations", {}).get("all")),
                "h_index": to_int(table.get("h_index", {}).get("all")),
                "i10_index": to_int(table.get("i10_index", {}).get("all")),
            }
        page = data.get("articles", [])
        for a in page:
            articles.append({
                "title": a.get("title", ""),
                "authors": a.get("authors", ""),
                "venue": a.get("publication", ""),
                "year": to_int(a.get("year")),
                "cited_by": to_int((a.get("cited_by") or {}).get("value")),
                "link": a.get("link", ""),
            })
        if len(page) < 100:
            break
        start += 100
    return metrics, articles


def parse_profile_page(page_html):
    """Parse a Google Scholar profile page into (metrics, articles)."""
    soup = BeautifulSoup(page_html, "html.parser")
    cells = [td.get_text() for td in soup.select("#gsc_rsb_st td.gsc_rsb_std")]
    metrics = {}
    if len(cells) >= 6:
        metrics = {
            "citations": to_int(cells[0]),
            "h_index": to_int(cells[2]),
            "i10_index": to_int(cells[4]),
        }
    articles = []
    for row in soup.select("tr.gsc_a_tr"):
        title_el = row.select_one("a.gsc_a_at")
        if not title_el:
            continue
        grays = row.select("div.gs_gray")
        venue = grays[1].get_text(" ", strip=True) if len(grays) > 1 else ""
        venue = re.sub(r"[\s,]*\d{4}$", "", venue).strip(" ,")  # Scholar appends the year
        href = title_el.get("href") or title_el.get("data-href") or ""
        articles.append({
            "title": title_el.get_text(strip=True),
            "authors": grays[0].get_text(strip=True) if grays else "",
            "venue": venue,
            "year": to_int(row.select_one(".gsc_a_y").get_text() if row.select_one(".gsc_a_y") else ""),
            "cited_by": to_int(row.select_one("a.gsc_a_ac").get_text() if row.select_one("a.gsc_a_ac") else ""),
            "link": "https://scholar.google.com" + href if href.startswith("/") else href,
        })
    return metrics, articles


def fetch_scholar_page():
    res = requests.get(
        "https://scholar.google.com/citations",
        params={"user": SCHOLAR_ID, "hl": "en", "sortby": "pubdate", "cstart": 0, "pagesize": 100},
        headers=HEADERS,
        timeout=60,
    )
    res.raise_for_status()
    return parse_profile_page(res.text)


def title_key(title):
    return re.sub(r"[^a-z0-9]+", "", html.unescape(title).lower())[:60]


def fmt(n):
    return f"{n:,}"


def set_marked(page, attr, value, text):
    """Replace the inner text of the element carrying attr="value"."""
    pattern = re.compile(
        rf'(<(\w+)\b[^>]*\b{attr}="{re.escape(value)}"[^>]*>)(.*?)(</\2>)', re.S
    )
    return pattern.sub(lambda m: m.group(1) + text + m.group(4), page)


def render_latest(articles):
    items = []
    for a in articles[:LATEST_COUNT]:
        authors = html.escape(a["authors"])
        authors = re.sub(
            rf"([A-Z]+ {OWNER_NAME})", r"<strong>\1</strong>", authors, flags=re.I
        )
        meta = " · ".join(x for x in [authors, html.escape(a["venue"]), str(a["year"] or "")] if x)
        link = html.escape(a["link"] or "https://scholar.google.com/citations?user=" + SCHOLAR_ID, quote=True)
        items.append(
            f'          <li><a href="{link}" target="_blank" rel="noopener">{html.escape(a["title"])}</a>'
            f"<span>{meta}</span></li>"
        )
    return '        <ul class="latest">\n' + "\n".join(items) + "\n        </ul>\n"


def update_page(page, metrics, articles, now):
    for key in ("citations", "h_index", "i10_index"):
        if metrics.get(key):
            page = set_marked(page, "data-scholar", key, fmt(metrics[key]))
    page = set_marked(page, "data-scholar", "updated", now.strftime("%B %Y"))

    # Cited-by badges on the selected publications
    by_key = {title_key(a["title"]): a for a in articles}

    def badge(m):
        key = m.group(1)
        match = by_key.get(key) or next(
            (a for k, a in by_key.items() if k.startswith(key[:45]) or key.startswith(k[:45])), None
        )
        if not match or not match["cited_by"]:
            return m.group(0)
        return f'<span class="cites" data-cites="{key}">Cited by {fmt(match["cited_by"])}</span>'

    page = re.sub(r'<span class="cites" data-cites="([a-z0-9]+)"(?: hidden)?>.*?</span>', badge, page)

    # Latest publications, newest first
    latest = sorted(articles, key=lambda a: a["year"], reverse=True)
    page = re.sub(
        r"(<!-- scholar:latest:start -->\n).*?(\s*<!-- scholar:latest:end -->)",
        lambda m: m.group(1) + render_latest(latest).rstrip("\n") + m.group(2),
        page,
        flags=re.S,
    )
    return page


def main():
    key = os.environ.get("SERPAPI_KEY", "").strip()
    try:
        metrics, articles = fetch_serpapi(key) if key else fetch_scholar_page()
    except requests.RequestException as err:
        print(f"::warning::Could not reach the data source: {err}. Nothing changed.")
        return 0

    if not metrics.get("citations") or not articles:
        print(
            "::warning::No usable data returned (Google Scholar may be blocking automated requests). "
            "Add a SERPAPI_KEY repository secret for reliable updates. Nothing changed."
        )
        return 0

    now = datetime.now(timezone.utc)
    page = INDEX.read_text(encoding="utf-8")
    INDEX.write_text(update_page(page, metrics, articles, now), encoding="utf-8")

    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(
        json.dumps({"updated": now.isoformat(timespec="seconds"), **metrics, "articles": articles}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(f"Updated: {metrics['citations']} citations, h-index {metrics['h_index']}, {len(articles)} publications.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
