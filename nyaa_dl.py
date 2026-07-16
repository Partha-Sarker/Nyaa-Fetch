import argparse
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://nyaa.si"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def sanitize(name):
    return re.sub(r'[/\\:*?"<>|]', "_", name).strip()


def parse_rows(soup):
    results = []
    for row in soup.select("tr"):
        view_link = row.select_one("a[href^='/view/']:not(.comments)")
        dl_link = row.select_one("a[href$='.torrent']")
        if not view_link or not dl_link:
            continue
        title = view_link.get("title") or view_link.get_text(strip=True)
        href = dl_link["href"]
        url = href if href.startswith("http") else BASE_URL + href
        results.append((sanitize(title), url))
    return results


def download(title, url, out_dir):
    dest = out_dir / f"{title}.torrent"
    if dest.exists():
        print(f"  skip (exists): {dest}")
        return
    response = requests.get(url, headers=HEADERS, stream=True)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"  downloaded: {dest}")


def main():
    parser = argparse.ArgumentParser(description="Download torrent files from a Nyaa.si page")
    parser.add_argument("url", help="Nyaa.si search or browse page URL")
    parser.add_argument("--dir", dest="out_dir", help="Output directory (default: first torrent title)")
    parser.add_argument("--filter", dest="filter_str", help="Only download torrents whose title contains this string (case-insensitive)")
    args = parser.parse_args()

    response = requests.get(args.url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = parse_rows(soup)

    if not rows:
        print("No torrent links found on that page.")
        sys.exit(1)

    if args.filter_str:
        needle = args.filter_str.lower()
        rows = [r for r in rows if needle in r[0].lower()]
        if not rows:
            print(f"No torrents matched filter: {args.filter_str!r}")
            sys.exit(1)

    out_dir = Path(args.out_dir) if args.out_dir else Path("downloads") / rows[0][0]
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving to: {out_dir}/\n")

    for title, url in rows:
        download(title, url, out_dir)

    print(f"\nDone. {len(rows)} torrent(s) processed.")


if __name__ == "__main__":
    main()
