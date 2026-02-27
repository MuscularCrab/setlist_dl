#!/usr/bin/env python3
"""
setlist-dl - Download individual tracks from DJ setlists
Cross-platform tool using yt-dlp with SoundCloud/YouTube fallback.

Usage:
    python setlist-dl.py                          # Interactive mode
    python setlist-dl.py setlists/my_setlist.json # Load a setlist file
    python setlist-dl.py --format mp3             # Override audio format
    python setlist-dl.py --output ~/Music/Set     # Override output directory
"""

import argparse
import json
import os
import subprocess
import sys
import shutil
from pathlib import Path

# ──────────────────────────────────────────────
# ANSI colors (auto-disabled on Windows < 10)
# ──────────────────────────────────────────────
def supports_color():
    if os.name == "nt":
        return os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM") == "vscode"
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

USE_COLOR = supports_color()

def c(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text

def green(t):  return c(t, "32")
def red(t):    return c(t, "31")
def yellow(t): return c(t, "33")
def cyan(t):   return c(t, "36")
def bold(t):   return c(t, "1")

# ──────────────────────────────────────────────
# yt-dlp version check
# ──────────────────────────────────────────────
def check_ytdlp():
    """Ensure yt-dlp is installed and reasonably up to date."""
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        print(red("ERROR: yt-dlp not found in PATH."))
        print()
        if os.name == "nt":
            print("Install on Windows:")
            print("  winget install yt-dlp")
            print("  OR: pip install yt-dlp")
            print("  OR: download from https://github.com/yt-dlp/yt-dlp/releases")
        else:
            print("Install on Linux:")
            print("  # Recommended: direct binary (always up to date)")
            print("  sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \\")
            print("       -o /usr/local/bin/yt-dlp && sudo chmod a+rx /usr/local/bin/yt-dlp")
            print()
            print("  # OR via pip:")
            print("  pip install yt-dlp")
            print()
            print("  # Avoid: sudo apt install yt-dlp  (usually outdated)")
        sys.exit(1)

    # Check version
    try:
        result = subprocess.run([ytdlp, "--version"], capture_output=True, text=True, timeout=10)
        version = result.stdout.strip()
        print(f"  yt-dlp version: {version}")

        # Warn if old (pre-2025)
        if version < "2025":
            print(yellow(f"  WARNING: yt-dlp {version} is outdated. SoundCloud/YouTube may fail."))
            print(yellow("  Update: yt-dlp -U  (or reinstall from GitHub releases)"))
            print()
    except Exception:
        print(yellow("  Could not determine yt-dlp version."))

    return ytdlp

# ──────────────────────────────────────────────
# ffmpeg check
# ──────────────────────────────────────────────
def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print(yellow("WARNING: ffmpeg not found. Audio conversion may fail."))
        if os.name == "nt":
            print("  Install: winget install ffmpeg")
        else:
            print("  Install: sudo apt install ffmpeg  (or your distro's package manager)")
        print()

# ──────────────────────────────────────────────
# Download a single track
# ──────────────────────────────────────────────
def download_track(query, track_num, output_dir, audio_format, ytdlp_path):
    """
    Try SoundCloud first, then YouTube. Returns True on success.
    """
    print()
    print(f"  [{bold(track_num)}] {cyan(query)}")
    print(f"  {'─' * 50}")

    yt_opts = [
        "-x",
        "--audio-format", audio_format,
        "--audio-quality", "0",
        "--embed-metadata",
        "--no-playlist",
        "--no-warnings",
        "-o", str(Path(output_dir) / f"{track_num}. %(title)s.%(ext)s"),
    ]

    # Source 1: SoundCloud
    print(f"  🔍 Searching SoundCloud...", end=" ", flush=True)
    result = subprocess.run(
        [ytdlp_path] + yt_opts + [f"scsearch1:{query}"],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode == 0 and "Downloading 1 items" not in result.stderr:
        # Double check it actually downloaded something
        if "has already been downloaded" in result.stdout or result.returncode == 0:
            # Verify no "0 items" in output
            combined = result.stdout + result.stderr
            if "0 videos" not in combined and "ERROR" not in combined:
                print(green("✓ Found"))
                return True

    # Source 2: YouTube
    print(yellow("✗"))
    print(f"  🔍 Searching YouTube...", end=" ", flush=True)
    result = subprocess.run(
        [ytdlp_path] + yt_opts + [f"ytsearch1:{query}"],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode == 0:
        combined = result.stdout + result.stderr
        if "ERROR" not in combined:
            print(green("✓ Found"))
            return True

    print(red("✗ NOT FOUND"))
    return False

# ──────────────────────────────────────────────
# Load / create setlist
# ──────────────────────────────────────────────
def load_setlist(path):
    """Load a JSON setlist file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def create_example_setlist():
    """Return the bundled Rebecca Black setlist."""
    return {
        "name": "Rebecca Black @ Boiler Room Washington, DC",
        "date": "2024-09-14",
        "source": "https://www.1001tracklists.com/tracklist/1xyv0pqk/",
        "audio_format": "wav",
        "output_dir_name": "Rebecca_Black_Boiler_Room_DC",
        "tracks": [
            {"num": "01", "query": "eurosanto I'm probably perfect"},
            {"num": "02", "query": "COBRAH VTSS MCR-T TITS LIPS HIPS KISS 10/10 Remix"},
            {"num": "03", "query": "SOPHIE Hard Boys Noize X&G Remix"},
            {"num": "04", "query": "Slayyyter Purrr Owen Jackson Remix"},
            {"num": "05", "query": "Justice Stress"},
            {"num": "06", "query": "Beyonce Yonce Mell Rave Edit"},
            {"num": "07", "query": "Joy Orbison Charli xcx Guess FM Cimarron Blend"},
            {"num": "08", "query": "COMANAVAGO Bjorkhain"},
            {"num": "09", "query": "Lily Rose Depp World Class Sinner SoFTT Edit"},
            {"num": "10", "query": "N Sync I Want You Back sowhy3 Edit"},
            {"num": "11", "query": "Megan Thee Stallion Thot Shit TAAHLIAH remix"},
            {"num": "12", "query": "dj g2g rude boy tokyo drift"},
            {"num": "13", "query": "Baauer All My Ladies"},
            {"num": "14", "query": "EDBOY HOLLABACK GURL"},
            {"num": "15", "query": "George Riley Hudson Mohawke S E X"},
            {"num": "16", "query": "Mika Heggemann Taucher Millennium Bitch"},
            {"num": "17", "query": "Yaeji booboo"},
            {"num": "18", "query": "Far East Movement Like A G6 Cimarron Jersey Flip"},
            {"num": "19", "query": "DJ G2G Joao Lagrima De Ouro Melo Do Yeah"},
            {"num": "20", "query": "Lana Del Rey Mariners Apartment Complex remix"},
            {"num": "21", "query": "Disclosure You and Me Flume Remix Heggemann Edit"},
            {"num": "22", "query": "Moodrich luv u nicki but ur beats r trash"},
            {"num": "23", "query": "Swank Mami Bad Bitch"},
            {"num": "24", "query": "Crazy Frog Axel F A.N.I. Rave Mix"},
            {"num": "25", "query": "COBRAH GOOEY FLUID GIRLS"},
            {"num": "26", "query": "Da Hool Meet Her At The Love Parade remix"},
            {"num": "27", "query": "Torren Foot Associanu Sleep When Im Dead LO99 Remix"},
            {"num": "28", "query": "Ethel Cain Romy Fred Again American Teenager Strong Jevan Mash"},
            {"num": "29", "query": "felipe.mp3 36Friday.mp3"},
        ]
    }

# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Download individual tracks from a DJ setlist using yt-dlp.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setlist-dl.py                                # Use bundled setlist
  python setlist-dl.py setlists/my_set.json           # Custom setlist
  python setlist-dl.py --format mp3 --output ./tracks # MP3 to ./tracks
  python setlist-dl.py --tracks 5-15                  # Download only tracks 5-15
  python setlist-dl.py --create-template out.json     # Generate a blank template
        """
    )
    parser.add_argument("setlist", nargs="?", help="Path to setlist JSON file (optional)")
    parser.add_argument("-f", "--format", choices=["wav", "mp3", "flac", "opus", "aac"],
                        help="Audio format (overrides setlist setting)")
    parser.add_argument("-o", "--output", help="Output directory (overrides setlist setting)")
    parser.add_argument("-t", "--tracks", help="Track range, e.g. '5-15' or '1,3,7'")
    parser.add_argument("--create-template", metavar="FILE",
                        help="Create a blank setlist template JSON and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded without downloading")

    args = parser.parse_args()

    # Create template mode
    if args.create_template:
        template = {
            "name": "Artist @ Venue",
            "date": "2024-01-01",
            "source": "https://www.1001tracklists.com/tracklist/...",
            "audio_format": "wav",
            "output_dir_name": "Artist_Venue",
            "tracks": [
                {"num": "01", "query": "Artist - Track Name"},
                {"num": "02", "query": "Artist - Track Name (Remix)"},
            ]
        }
        with open(args.create_template, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"Template created: {args.create_template}")
        sys.exit(0)

    # Banner
    print()
    print(bold("╔══════════════════════════════════════════════╗"))
    print(bold("║        setlist-dl — Setlist Track Grabber    ║"))
    print(bold("║   SoundCloud → YouTube fallback via yt-dlp   ║"))
    print(bold("╚══════════════════════════════════════════════╝"))
    print()

    # Load setlist
    if args.setlist:
        print(f"  Loading: {args.setlist}")
        setlist = load_setlist(args.setlist)
    else:
        print("  Using bundled setlist: Rebecca Black @ Boiler Room DC 2024")
        setlist = create_example_setlist()

    print(f"  Set:    {setlist['name']}")
    print(f"  Date:   {setlist.get('date', 'Unknown')}")
    print(f"  Tracks: {len(setlist['tracks'])}")
    print()

    # Check dependencies
    ytdlp_path = check_ytdlp()
    check_ffmpeg()

    # Resolve settings
    audio_format = args.format or setlist.get("audio_format", "wav")
    if args.output:
        output_dir = args.output
    else:
        music_base = Path.home() / "Music"
        output_dir = str(music_base / setlist.get("output_dir_name", "setlist-dl-output"))

    print(f"  Format: {bold(audio_format)}")
    print(f"  Output: {bold(output_dir)}")

    # Parse track range
    tracks = setlist["tracks"]
    if args.tracks:
        if "-" in args.tracks:
            start, end = args.tracks.split("-", 1)
            tracks = [t for t in tracks if int(start) <= int(t["num"]) <= int(end)]
        elif "," in args.tracks:
            nums = set(args.tracks.split(","))
            tracks = [t for t in tracks if t["num"].lstrip("0") in nums or t["num"] in nums]
        print(f"  Range:  {len(tracks)} tracks selected")

    print()

    if args.dry_run:
        print(bold("  DRY RUN — would download:"))
        for t in tracks:
            print(f"    [{t['num']}] {t['query']}")
        sys.exit(0)

    # Create output dir
    os.makedirs(output_dir, exist_ok=True)

    # Download
    missing_file = Path(output_dir) / "_MISSING_TRACKS.txt"
    missing_file.write_text("", encoding="utf-8")

    success = 0
    failed = 0
    missing = []

    for track in tracks:
        try:
            ok = download_track(track["query"], track["num"], output_dir, audio_format, ytdlp_path)
        except subprocess.TimeoutExpired:
            print(red("  ✗ TIMEOUT"))
            ok = False
        except Exception as e:
            print(red(f"  ✗ ERROR: {e}"))
            ok = False

        if ok:
            success += 1
        else:
            failed += 1
            missing.append(track)
            with open(missing_file, "a", encoding="utf-8") as f:
                f.write(f"[{track['num']}] {track['query']}\n")

    # Summary
    print()
    print(bold("══════════════════════════════════════════════"))
    print(bold("  RESULTS"))
    print(f"  {green(f'✓ {success} downloaded')}  |  {red(f'✗ {failed} missing') if failed else green('0 missing')}")
    print(f"  Output: {output_dir}")

    if missing:
        print()
        print(yellow("  Missing tracks (saved to _MISSING_TRACKS.txt):"))
        for t in missing:
            print(f"    [{t['num']}] {t['query']}")

    print(bold("══════════════════════════════════════════════"))
    print()

if __name__ == "__main__":
    main()
