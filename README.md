# nyaa-fetch

Downloads all torrent files listed on a Nyaa.si search/browse page.

## Setup

Python 3 is required (`python3`). Because macOS Homebrew manages the system Python, install dependencies inside a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4
```

After the first setup, activate the venv before each session:

```bash
source .venv/bin/activate
```

## Usage

```bash
python3 nyaa_dl.py <url> [--dir <output_dir>]
```

| Argument | Description |
|----------|-------------|
| `url` | Nyaa.si search or browse page URL |
| `--dir` | Directory to save `.torrent` files into. Defaults to the title of the first torrent found. |

## Examples

```bash
# Auto-named directory under downloads/ (uses first torrent's title)
python3 nyaa_dl.py "https://nyaa.si/?f=0&c=1_2&q=%5BJudas%5D+Dia+no+Ace+-+S04"

# Custom output directory
python3 nyaa_dl.py "https://nyaa.si/?f=0&c=1_2&q=one+piece" --dir ./one-piece-torrents
```

The script prints each downloaded file path and skips files that already exist in the output directory.
