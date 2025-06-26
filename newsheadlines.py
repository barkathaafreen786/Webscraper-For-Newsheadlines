

import argparse
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.bbc.com/news"
DEFAULT_LIMIT = 10
OUTPUT_FILE = Path("headlines.txt")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; InternshipNewsBot/1.0; "
        "+https://github.com/your-username)"
    )
}


def fetch_html(url: str) -> str:
    """Fetch raw HTML from a URL and return its text, raising for bad status."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as err:
        sys.exit(f"[ERROR] Failed to fetch {url}: {err}")


def parse_headlines(html: str, limit: int) -> list[str]:
    """Parse HTML and return up to *limit* headline strings."""
    soup = BeautifulSoup(html, "html.parser")

    # Grab common headline tags first
    headlines = [h.get_text(strip=True) for h in soup.find_all("h2")]
    # Fallback to <title> tags if <h2> were scarce
    if len(headlines) < limit:
        headlines.extend(
            t.get_text(strip=True) for t in soup.find_all("title")
        )

    # De-duplicate while preserving order
    seen: set[str] = set()
    unique_headlines = []
    for text in headlines:
        if text and text not in seen:
            seen.add(text)
            unique_headlines.append(text)
        if len(unique_headlines) >= limit:
            break
    return unique_headlines


def save_headlines(headlines: list[str], file: Path = OUTPUT_FILE) -> None:
    """Write one headline per line to *file*."""
    file.write_text("\n".join(headlines), encoding="utf-8")
    print(f"[✓] Saved {len(headlines)} headlines to {file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple news headline scraper.")
    parser.add_argument("--url", default=DEFAULT_URL, help="News site URL to scrape")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help="Number of headlines to save (default 10)")
    args = parser.parse_args()

    html = fetch_html(args.url)
    headlines = parse_headlines(html, args.limit)
    if not headlines:
        sys.exit("[!] No headlines found — check the URL or parsing logic.")

    save_headlines(headlines)


if __name__ == "__main__":
    main()
