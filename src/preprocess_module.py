"""
Pre-process module — Section 6.4.2 of the original report.

Provides two classes:

* ``TokenizeSentences`` — splits the raw input text into sentences and words
  using NLTK.
* ``Preprocess`` — builds the word-frequency table after stopword removal and
  Porter stemming.
"""

from __future__ import annotations

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize


class TokenizeSentences:
    """Tokenise a document into sentences and words.

    Matches the original report's interface:

        tobj = TokenizeSentences(text)
        tobj.getTokens()                  # populates self.sentences
        tobj.tokenizeWords(text)          # populates self.words
    """

    def __init__(self, input_data: str) -> None:
        self.input_data = input_data
        self.words: list[str] = []
        self.sentences: list[str] = []

    def getTokens(self) -> None:  # noqa: N802 (preserve original API casing)
        self.sentences = sent_tokenize(self.input_data)

    def tokenizeWords(self, text: str) -> None:  # noqa: N802
        self.words = word_tokenize(text)


class Preprocess:
    """Build a word-frequency table from tokenised words.

    Steps:
        1. Drop stopwords (NLTK English list) and a small set of symbols.
        2. Stem each remaining word with the Porter stemmer.
        3. Count frequencies.
    """

    def __init__(self) -> None:
        self.frequency_table: dict[str, int] = {}
        self.symbols = ["\n", " ", "!", ",", ".", "?", ";", ":", "(", ")", "[", "]"]

    def filterDocument(self, tkn: TokenizeSentences) -> dict[str, int]:  # noqa: N802
        stop_words = set(stopwords.words("english"))
        stemmer = PorterStemmer()

        for raw in tkn.words:
            wd = stemmer.stem(raw.lower())
            if wd in stop_words or wd in self.symbols or not wd.strip():
                continue
            self.frequency_table[wd] = self.frequency_table.get(wd, 0) + 1

        return self.frequency_table
