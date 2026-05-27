"""
Feature Extraction module — Section 6.4.3 of the original report.

``SentenceScoring`` assigns a numeric importance score to every sentence
in the document. The score combines two signals:

1. Sum of stemmed-word frequencies, normalised by a running counter
   (the report calls this "tfidf" — it is an approximation, not a true
   TF-IDF score).
2. A proper-noun boost: count of ``NNP`` / ``NNPS`` POS tags in the
   sentence divided by the total proper-noun count across the document.

Compared to the original report this implementation fixes one obvious
bug: the proper-noun counter is now reset per-sentence so the boost is
actually per-sentence (in the original, ``sncount`` accumulated across
the entire loop). Output remains qualitatively the same.
"""

from __future__ import annotations

import nltk
from nltk.tokenize import word_tokenize

from .preprocess_module import Preprocess, TokenizeSentences


class SentenceScoring:
    """Score sentences using frequency + proper-noun POS tag features."""

    def __init__(self) -> None:
        self.sentence_score: dict[str, float] = {}
        self.tfidf = 0

    def calculateScore(  # noqa: N802 (preserve original API)
        self, tkn: TokenizeSentences, pre: Preprocess
    ) -> None:
        # --- Stage 1: frequency-based score --------------------------------
        for sentence in tkn.sentences:
            lowered = sentence.lower()
            for word, weight in pre.frequency_table.items():
                self.tfidf += 1
                if word in lowered:
                    self.sentence_score[sentence] = (
                        self.sentence_score.get(sentence, 0) + weight
                    )

            if sentence in self.sentence_score and self.tfidf > 0:
                self.sentence_score[sentence] = (
                    self.sentence_score[sentence] / self.tfidf
                )

        # --- Stage 2: proper-noun boost ------------------------------------
        total_proper_nouns = 0
        for sentence in tkn.sentences:
            pos_tags = nltk.pos_tag(word_tokenize(sentence))
            total_proper_nouns += sum(
                1 for _, tag in pos_tags if tag in {"NNP", "NNPS"}
            )

        if total_proper_nouns == 0:
            return

        for sentence in tkn.sentences:
            pos_tags = nltk.pos_tag(word_tokenize(sentence))
            local = sum(1 for _, tag in pos_tags if tag in {"NNP", "NNPS"})
            self.sentence_score[sentence] = (
                self.sentence_score.get(sentence, 0) + (local / total_proper_nouns)
            )

    def returnScore(self) -> dict[str, float]:  # noqa: N802
        return self.sentence_score
