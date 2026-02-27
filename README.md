##VIBE CODED

# setlist-dl

Download individual tracks from DJ setlists for mixing. Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) to search SoundCloud first, then falls back to YouTube — ideal for grabbing bootleg edits, unofficial remixes, and underground tracks that live on SoundCloud.

Built for DJs who find setlists on [1001tracklists](https://www.1001tracklists.com/) and want to grab every track without clicking through dozens of pages.

## Features

- **Dual-source fallback** — SoundCloud → YouTube automatic failover
- **DJ-ready formats** — WAV (default), FLAC, MP3, AAC, Opus
- **Numbered output** — files prefixed `01.`, `02.`, etc. matching setlist order
- **Missing track log** — anything not found is saved to `_MISSING_TRACKS.txt`
- **Cross-platform** — works on Linux, Windows, and macOS
- **No pip dependencies** — pure Python 3.7+ stdlib (just needs yt-dlp + ffmpeg installed)
- **JSON setlists** — easy to create, share, and version control
- **Track range selection** — download only specific tracks with `--tracks 5-15`
- **Dry run mode** — preview what will be downloaded with `--dry-run`

## Quick Start

```bash
# Clone the repo
git clone https://github.com/MuscularCrab/setlist-dl.git
cd setlist-dl

# Run with the included example setlist
python setlist-dl.py

# Or load a specific setlist
python setlist-dl.py setlists/rebecca_black_boiler_room_dc_2024.json
```

## Installation

### Prerequisites

You need **yt-dlp** and **ffmpeg** installed. The Python script itself has zero pip dependencies.

---

### Linux (Ubuntu / Debian / CachyOS / Arch)

**yt-dlp** — install the latest binary directly (the `apt` version is usually ancient and broken):

```bash
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
     -o /usr/local/bin/yt-dlp && sudo chmod a+rx /usr/local/bin/yt-dlp
```

Or on Arch/CachyOS:
```bash
sudo pacman -S yt-dlp
```

**ffmpeg:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Arch/CachyOS
sudo pacman -S ffmpeg
```

**Run:**
```bash
chmod +x setlist-dl.sh
./setlist-dl.sh
# or: python3 setlist-dl.py
```

> **⚠️ Avoid `sudo apt install yt-dlp`** on Ubuntu/Debian — the packaged version is typically 1-2 years behind and has broken SoundCloud/YouTube extractors. Always use the GitHub binary or `pip install yt-dlp`.

---

### Windows

**yt-dlp:**
```powershell
# Option 1: winget (recommended)
winget install yt-dlp

# Option 2: pip
pip install yt-dlp

# Option 3: Download .exe from GitHub releases
# https://github.com/yt-dlp/yt-dlp/releases
```

**ffmpeg:**
```powershell
winget install ffmpeg
```

**Run:**
```powershell
# Double-click setlist-dl.bat
# Or from terminal:
python setlist-dl.py
```

---

### macOS

```bash
brew install yt-dlp ffmpeg
python3 setlist-dl.py
```

## Usage

```
python setlist-dl.py [OPTIONS] [SETLIST_FILE]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `SETLIST_FILE` | Path to a JSON setlist file (optional — uses bundled setlist if omitted) |

### Options

| Flag | Description |
|------|-------------|
| `-f`, `--format` | Audio format: `wav` `mp3` `flac` `opus` `aac` (default: `wav`) |
| `-o`, `--output` | Output directory (default: `~/Music/<setlist_name>`) |
| `-t`, `--tracks` | Track range: `5-15` or `1,3,7` |
| `--create-template FILE` | Generate a blank setlist JSON template |
| `--dry-run` | Show what would be downloaded without downloading |

### Examples

```bash
# Download all tracks as WAV (default)
python setlist-dl.py setlists/my_set.json

# Download as MP3 to a specific folder
python setlist-dl.py -f mp3 -o ./tracks setlists/my_set.json

# Download only tracks 10-20
python setlist-dl.py -t 10-20 setlists/my_set.json

# Download specific tracks
python setlist-dl.py -t 1,5,12,29 setlists/my_set.json

# Preview without downloading
python setlist-dl.py --dry-run setlists/my_set.json

# Create a blank template to fill in
python setlist-dl.py --create-template setlists/my_new_set.json
```

## Creating Setlists

Setlists are simple JSON files. Create one from a template:

```bash
python setlist-dl.py --create-template setlists/my_set.json
```

Then edit it:

```json
{
  "name": "DJ Name @ Venue",
  "date": "2024-01-01",
  "source": "https://www.1001tracklists.com/tracklist/...",
  "audio_format": "wav",
  "output_dir_name": "DJ_Name_Venue",
  "tracks": [
    {"num": "01", "query": "Artist - Track Name"},
    {"num": "02", "query": "Artist - Track Name (Remix Artist Remix)"},
    {"num": "03", "query": "Artist feat. Other - Track (DJ Edit)"}
  ]
}
```

### Setlist Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the setlist |
| `date` | No | Date of the set (YYYY-MM-DD) |
| `source` | No | URL to the original tracklist |
| `audio_format` | No | Default format (`wav`, `mp3`, `flac`, `opus`, `aac`) |
| `output_dir_name` | No | Folder name under `~/Music/` |
| `tracks` | Yes | Array of track objects |

### Track Fields

| Field | Required | Description |
|-------|----------|-------------|
| `num` | Yes | Track number, zero-padded (`"01"`, `"02"`, ...) |
| `query` | Yes | Search query — typically `"Artist Title Remix"` |

### Tips for Search Queries

- **Include the remix/edit artist**: `"SOPHIE Hard Boys Noize X&G Remix"` works better than just `"SOPHIE Hard"`
- **Use the edit name**: `"Beyonce Yonce Mell Rave Edit"` — bootleg edits are often titled this way on SoundCloud
- **Try variations**: if a track isn't found, edit the query in the JSON and re-run with `--tracks` to retry just that one
- **SoundCloud-first strategy**: many DJ edits, bootlegs, and unofficial remixes only exist on SoundCloud, which is why it's searched first

## Output

Downloaded tracks are saved as:
```
~/Music/<output_dir_name>/
├── 01. Track Title.wav
├── 02. Another Track.wav
├── ...
└── _MISSING_TRACKS.txt     # tracks that couldn't be found
```

The `_MISSING_TRACKS.txt` file lists anything that failed, so you can hunt those down manually.

## Troubleshooting

### "SoundCloud failed" on every track
Your yt-dlp is outdated. The SoundCloud extractor breaks frequently and needs the latest version.

```bash
# Update yt-dlp
yt-dlp -U

# Or reinstall from GitHub
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
     -o /usr/local/bin/yt-dlp && sudo chmod a+rx /usr/local/bin/yt-dlp
```

### "Sign in to confirm you're not a bot" (YouTube)
Also caused by outdated yt-dlp. Update to the latest version.

### "ffmpeg not found"
Install ffmpeg — it's required for audio conversion:
```bash
# Linux
sudo apt install ffmpeg

# Windows
winget install ffmpeg

# macOS
brew install ffmpeg
```

### Track downloads but is wrong
Edit the `query` field in your setlist JSON to be more specific. Adding remix artist names, label names, or "(Official Audio)" can help.

### False positives (shows "Downloaded" but file is empty/wrong)
Re-run with `--tracks` targeting just those track numbers after updating yt-dlp.

## Included Setlists

| File | Set |
|------|-----|
| `rebecca_black_boiler_room_dc_2024.json` | Rebecca Black @ Boiler Room Washington, DC (2024-09-14) — 29 tracks, Dance/Electro Pop/Techno |

PRs with more setlists are welcome!

## Contributing

1. Fork the repo
2. Add setlists to `setlists/` following the JSON format above
3. Name files as `artist_venue_year.json` (lowercase, underscores)
4. Submit a PR

## License

MIT — see [LICENSE](LICENSE).
