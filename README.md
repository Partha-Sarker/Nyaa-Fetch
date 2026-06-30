# nyaa-fetch

Downloads all torrent files listed on a Nyaa.si search/browse page.

## Requirements

Python 3 (`python3`) must be installed. Everything else is handled automatically.

## Usage

```bash
./nyaa-fetch.sh <url> [--dir <output_dir>]
```

On first run the script creates a virtual environment and installs dependencies silently. Subsequent runs skip straight to downloading.

| Argument | Description |
|----------|-------------|
| `url` | Nyaa.si search or browse page URL |
| `--dir` | Directory to save `.torrent` files into. Defaults to `downloads/<first torrent title>`. |

## Examples

```bash
# Auto-named directory under downloads/
./nyaa-fetch.sh "https://nyaa.si/?f=0&c=1_2&q=%5BJudas%5D+Dia+no+Ace+-+S04"

# Custom output directory
./nyaa-fetch.sh "https://nyaa.si/?f=0&c=1_2&q=one+piece" --dir ./one-piece-torrents
```

The script prints each downloaded file path and skips files that already exist in the output directory.
