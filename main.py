"""
Command-line entry point for the Text Summarizer.

Examples
--------
Summarize a local text file::

    python main.py --file data/sample.txt

Summarize a Wikipedia article::

    python main.py --url https://en.wikipedia.org/wiki/Natural_language_processing

Launch the original Tkinter GUI::

    python main.py --gui
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.summarizer import summarize, summarize_url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extractive text summarizer (NLP).")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--file", type=Path, help="Path to a local .txt file.")
    source.add_argument("--url", type=str, help="HTTP(S) URL of an article to fetch.")
    source.add_argument("--gui", action="store_true", help="Launch the Tkinter GUI.")
    parser.add_argument(
        "--top-n", type=int, default=3, help="How many sentences in the summary."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.gui:
        from src.gui import main as launch_gui

        launch_gui()
        return 0

    if args.file:
        text = args.file.read_text(encoding="utf-8")
        print(summarize(text, top_n=args.top_n))
        return 0

    if args.url:
        print(summarize_url(args.url, top_n=args.top_n))
        return 0

    print(
        "Please pass one of --file, --url, or --gui.\n"
        "Example: python main.py --file data/sample.txt",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
