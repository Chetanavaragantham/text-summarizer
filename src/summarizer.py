"""
High-level summarize() helper.

Wires the four modules together so callers can do::

    from src.summarizer import summarize
    print(summarize(open("article.txt").read(), top_n=3))

This is the headless, scriptable API. The original Tkinter GUI is
preserved in ``src.gui`` for reference but is not required.
"""

from __future__ import annotations

import urllib.request

from bs4 import BeautifulSoup

from .cluster_module import MakeClusters
from .feature_extraction_module import SentenceScoring
from .preprocess_module import Preprocess, TokenizeSentences


def _ensure_nltk_data() -> None:
    """Download NLTK corpora on first run.

    The original ``InterfaceModule`` calls these unconditionally. We do it
    lazily so test runs don't re-download on every invocation.
    """
    import nltk

    required = {
        "punkt": "tokenizers/punkt",
        "punkt_tab": "tokenizers/punkt_tab",
        "stopwords": "corpora/stopwords",
        "averaged_perceptron_tagger": "taggers/averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng": "taggers/averaged_perceptron_tagger_eng",
    }
    for pkg, path in required.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)


def summarize(text: str, top_n: int = 3) -> str:
    """Summarize a block of plain text.

    Parameters
    ----------
    text : str
        The full input document.
    top_n : int
        How many sentences the summary should contain (default 3, as in
        the original report).

    Returns
    -------
    str
        The summary sentences, separated by newlines.
    """
    _ensure_nltk_data()

    # 1. Tokenise.
    tkn = TokenizeSentences(text)
    tkn.getTokens()
    tkn.tokenizeWords(text)

    if not tkn.sentences:
        return ""

    # 2. Pre-process — build the frequency table.
    pre = Preprocess()
    pre.filterDocument(tkn)

    # 3. Score sentences.
    scoring = SentenceScoring()
    scoring.calculateScore(tkn, pre)
    scores = scoring.returnScore()

    if not scores:
        return ""

    # 4. Cluster and pick the top sentences.
    clusters = MakeClusters()
    clusters.formClusters(scores)
    return clusters.chooseSentences(scores, top_n=top_n)


def summarize_url(url: str, top_n: int = 3) -> str:
    """Fetch an HTML page, extract its <p> tags, and summarize."""
    with urllib.request.urlopen(url) as response:  # noqa: S310 (intentional)
        raw_html = response.read()

    soup = BeautifulSoup(raw_html, "html.parser")
    text = "\n".join(paragraph.get_text() for paragraph in soup.find_all("p"))
    return summarize(text, top_n=top_n)
