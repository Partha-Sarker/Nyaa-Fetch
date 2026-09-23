# nyaa-fetch

Downloads all torrent files listed on a Nyaa.si search/browse page.

## Requirements

- Python 3 (`python3`)
- Dependencies listed in [`requirements.txt`](requirements.txt):
  - `requests`
  - `beautifulsoup4`

> [!NOTE]
> You do **not** need to set up anything manually. The included wrapper script [`nyaa-fetch.sh`](nyaa-fetch.sh) automatically creates the virtual environment, activates it, and installs all dependencies from `requirements.txt`.

## Usage

### Quick Start (Recommended)

Simply run the script with a Nyaa.si URL:

```bash
./nyaa-fetch.sh <url> [--dir <output_dir>] [--filter <substring>]
```

On first run (or if the virtual environment is missing/broken), `nyaa-fetch.sh` does all the heavy lifting automatically:
1. **Creates** a virtual environment (`.venv`)
2. **Activates** the virtual environment
3. **Installs** all dependencies from [`requirements.txt`](requirements.txt)
4. **Executes** the download

Subsequent runs skip straight to downloading.

---

### Manual Setup & Running Directly with Python (Optional)

If you prefer to run `nyaa_dl.py` directly without the bash wrapper:

```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the script
python3 nyaa_dl.py <url> [--dir <output_dir>] [--filter <substring>]
```

---

## Options

| Argument | Description |
|----------|-------------|
| `url` | Nyaa.si search or browse page URL |
| `--dir` | Directory to save `.torrent` files into. Defaults to `downloads/<first torrent title>`. |
| `--filter` | Only download torrents whose title contains this string (case-insensitive). |

## Examples

```bash
# Auto-named directory under downloads/
./nyaa-fetch.sh "https://nyaa.si/?f=0&c=1_2&q=%5BJudas%5D+Dia+no+Ace+-+S04"

# Custom output directory
./nyaa-fetch.sh "https://nyaa.si/?f=0&c=1_2&q=one+piece" --dir ./one-piece-torrents

# Only download 1080p WEBRip releases
./nyaa-fetch.sh "https://nyaa.si/?f=0&c=1_2&q=one+piece" --filter "1080p WEBRip"
```

The script prints each downloaded file path and skips files that already exist in the output directory.
