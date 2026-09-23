import argparse
import concurrent.futures
import re
import sys
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
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


def download(session, title, url, out_dir):
    dest = out_dir / f"{title}.torrent"
    if dest.exists():
        return ("skip", dest, None)
    try:
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        dest.write_bytes(response.content)
        return ("downloaded", dest, None)
    except Exception as e:
        return ("failed", dest, str(e))


def main():
    parser = argparse.ArgumentParser(description="Download torrent files from a Nyaa.si page")
    parser.add_argument("url", help="Nyaa.si search or browse page URL")
    parser.add_argument("--dir", dest="out_dir", help="Output directory (default: first torrent title)")
    parser.add_argument("--filter", dest="filter_str", help="Only download torrents whose title contains this string (case-insensitive)")
    parser.add_argument(
        "-t",
        "--threads",
        dest="threads",
        type=int,
        default=5,
        help="Number of concurrent download threads (default: 5)",
    )
    args = parser.parse_args()

    if args.threads < 1:
        parser.error("--threads must be at least 1")

    session = requests.Session()
    session.headers.update(HEADERS)
    adapter = HTTPAdapter(pool_connections=args.threads, pool_maxsize=args.threads)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = session.get(args.url, timeout=30)
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

    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    max_workers = min(args.threads, len(rows))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_torrent = {
            executor.submit(download, session, title, url, out_dir): (title, url)
            for title, url in rows
        }
        for future in concurrent.futures.as_completed(future_to_torrent):
            status, dest, err = future.result()
            if status == "downloaded":
                print(f"  downloaded: {dest}")
                downloaded_count += 1
            elif status == "skip":
                print(f"  skip (exists): {dest}")
                skipped_count += 1
            elif status == "failed":
                print(f"  failed: {dest} ({err})")
                failed_count += 1

    summary_parts = [f"{downloaded_count} downloaded", f"{skipped_count} skipped"]
    if failed_count:
        summary_parts.append(f"{failed_count} failed")
    print(f"\nDone. {len(rows)} torrent(s) processed ({', '.join(summary_parts)}).")

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
