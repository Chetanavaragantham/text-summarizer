"""
Tkinter GUI — preserved from the original report (Section 6.4.1).

This is the desktop interface students saw during the demo. It exposes
two input modes (a local text file or an HTML URL) and a "Download
Summary" button that exports a PDF using FPDF.

Run with::

    python -m src.gui

The headless, scriptable equivalent lives in ``src.summarizer``.
"""

from __future__ import annotations

import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import filedialog, messagebox

from bs4 import BeautifulSoup
from fpdf import FPDF

from .summarizer import summarize


class SummarizerApp:
    """Top-level Tkinter window for the summarizer."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Text Summarizer")
        self.root.geometry("1000x800")

        self.location = tk.StringVar()
        self.use_local = tk.IntVar()
        self.use_url = tk.IntVar()

        self._build_widgets()

    def _build_widgets(self) -> None:
        title = tk.Label(
            self.root,
            text="TEXT SUMMARIZER",
            fg="blue",
            font=("Helvetica", 28, "bold"),
        )
        title.pack(pady=20)

        prompt = tk.Label(
            self.root,
            text="Please enter the location of local file or web page URL:",
            fg="#df74e9",
            font=("Helvetica", 12),
        )
        prompt.pack()

        self.entry = tk.Entry(
            self.root,
            width=80,
            fg="#336d92",
            font=("Helvetica", 12),
            textvariable=self.location,
        )
        self.entry.pack(pady=10)

        type_label = tk.Label(
            self.root,
            text="Please select the Input Type:",
            fg="#29472a",
            font=("Helvetica", 12),
        )
        type_label.pack()

        check_frame = tk.Frame(self.root)
        check_frame.pack(pady=5)

        local_chk = tk.Checkbutton(
            check_frame, text="Local Document", variable=self.use_local
        )
        local_chk.pack(side=tk.LEFT, padx=10)

        url_chk = tk.Checkbutton(
            check_frame, text="HTML web resource", variable=self.use_url
        )
        url_chk.pack(side=tk.LEFT, padx=10)

        browse_btn = tk.Button(
            self.root, text="Browse local file", command=self._browse
        )
        browse_btn.pack(pady=5)

        summarize_btn = tk.Button(
            self.root,
            text="Summarize",
            font=("Helvetica", 14, "bold"),
            command=self._on_summarize_click,
        )
        summarize_btn.pack(pady=10)

        download_btn = tk.Button(
            self.root,
            text="Download Summary",
            fg="#a464ff",
            font=("Helvetica", 14, "bold"),
            command=self._save_pdf,
        )
        download_btn.pack(pady=5)

        self.summary_output = tk.Text(
            self.root,
            bg="#29472a",
            fg="white",
            font=("Helvetica", 12),
            height=20,
            width=110,
        )
        self.summary_output.pack(pady=20)

    # --- Event handlers ----------------------------------------------------

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.location.set(path)

    def _read_input(self) -> str | None:
        path_or_url = self.location.get().strip()
        if not path_or_url:
            messagebox.showwarning("Missing input", "Please enter a path or URL.")
            return None

        if self.use_local.get() == 1 and self.use_url.get() == 0:
            try:
                return Path(path_or_url).read_text(encoding="utf-8")
            except OSError as exc:
                messagebox.showerror("Read error", str(exc))
                return None

        if self.use_url.get() == 1 and self.use_local.get() == 0:
            try:
                with urllib.request.urlopen(path_or_url) as response:  # noqa: S310
                    html = response.read()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Fetch error", str(exc))
                return None
            soup = BeautifulSoup(html, "html.parser")
            return "\n".join(p.get_text() for p in soup.find_all("p"))

        messagebox.showwarning(
            "Choose one input type",
            "Tick exactly one of 'Local Document' or 'HTML web resource'.",
        )
        return None

    def _on_summarize_click(self) -> None:
        text = self._read_input()
        if text is None:
            return

        summary = summarize(text)
        self.summary_output.delete("1.0", tk.END)
        self.summary_output.insert(tk.END, summary or "Choose a proper source!")

    def _save_pdf(self) -> None:
        summary = self.summary_output.get("1.0", tk.END).strip()
        if not summary:
            messagebox.showwarning("Nothing to export", "Run Summarize first.")
            return

        pdf = FPDF("L", "mm", "A4")
        pdf.add_page()
        pdf.set_font("Helvetica", size=20)
        pdf.cell(0, 10, txt="SUMMARY", align="C")
        pdf.ln(10)
        pdf.set_font("Helvetica", size=12)
        for line in summary.splitlines():
            pdf.multi_cell(0, 8, txt=line)
        out_path = Path("output.pdf")
        pdf.output(str(out_path))
        messagebox.showinfo("Saved", f"Summary saved to {out_path.resolve()}")


def main() -> None:
    root = tk.Tk()
    SummarizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
