import argparse
import concurrent.futures
import re
import sys
import urllib.parse
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


def parse_rows(soup, current_url=BASE_URL):
    results = []
    for row in soup.select("tr"):
        view_link = row.select_one("a[href^='/view/']:not(.comments)")
        dl_link = row.select_one("a[href$='.torrent']")
        if not view_link or not dl_link:
            continue
        title = view_link.get("title") or view_link.get_text(strip=True)
        href = dl_link["href"]
        url = urllib.parse.urljoin(current_url, href)
        results.append((sanitize(title), url))
    return results


def get_next_page_url(soup, current_url):
    next_li = soup.select_one("ul.pagination li.next")
    if not next_li or "disabled" in next_li.get("class", []):
        return None
    a_tag = next_li.find("a", href=True)
    if not a_tag or not a_tag.get("href"):
        return None
    return urllib.parse.urljoin(current_url, a_tag["href"])


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
        "--max-pages",
        dest="max_pages",
        type=int,
        default=None,
        help="Maximum number of pages to fetch (default: all pages)",
    )
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
    if args.max_pages is not None and args.max_pages < 1:
        parser.error("--max-pages must be at least 1")

    session = requests.Session()
    session.headers.update(HEADERS)
    adapter = HTTPAdapter(pool_connections=args.threads, pool_maxsize=args.threads)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    rows = []
    seen_urls = set()
    current_url = args.url
    page_num = 1

    while current_url:
        print(f"[Page {page_num}] Fetching: {current_url}")
        try:
            response = session.get(current_url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            if page_num == 1:
                print(f"Failed to fetch initial page: {e}")
                sys.exit(1)
            else:
                print(f"Failed to fetch page {page_num} ({e}), stopping pagination.")
                break

        soup = BeautifulSoup(response.text, "html.parser")
        page_rows = parse_rows(soup, current_url)

        new_count = 0
        for title, url in page_rows:
            if url not in seen_urls:
                seen_urls.add(url)
                rows.append((title, url))
                new_count += 1

        print(f"  Found {len(page_rows)} torrent(s) on page {page_num} ({new_count} new).")

        if args.max_pages and page_num >= args.max_pages:
            print(f"Reached page limit (--max-pages {args.max_pages}).")
            break

        next_url = get_next_page_url(soup, current_url)
        if not next_url or next_url == current_url:
            break

        current_url = next_url
        page_num += 1

    if not rows:
        print("No torrent links found.")
        sys.exit(1)

    print(f"\nTotal: {len(rows)} torrent(s) found across {page_num} page(s).")

    if args.filter_str:
        needle = args.filter_str.lower()
        rows = [r for r in rows if needle in r[0].lower()]
        if not rows:
            print(f"No torrents matched filter: {args.filter_str!r}")
            sys.exit(1)
        print(f"Filtered down to {len(rows)} torrent(s) matching: {args.filter_str!r}")

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
