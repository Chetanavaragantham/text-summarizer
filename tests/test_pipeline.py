"""
Smoke tests for the four-module summarizer pipeline.

Run with::

    pytest -q
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cluster_module import MakeClusters
from src.feature_extraction_module import SentenceScoring
from src.preprocess_module import Preprocess, TokenizeSentences
from src.summarizer import summarize

SAMPLE = (Path(__file__).resolve().parent.parent / "data" / "sample.txt").read_text()


def test_tokenize_sentences_produces_sentences():
    tkn = TokenizeSentences(SAMPLE)
    tkn.getTokens()
    assert len(tkn.sentences) > 3


def test_preprocess_builds_frequency_table():
    tkn = TokenizeSentences(SAMPLE)
    tkn.getTokens()
    tkn.tokenizeWords(SAMPLE)

    pre = Preprocess()
    table = pre.filterDocument(tkn)

    assert table  # not empty
    # All values are positive integers.
    assert all(isinstance(count, int) and count > 0 for count in table.values())
    # Stopwords should have been removed.
    assert "the" not in table
    assert "and" not in table


def test_sentence_scoring_assigns_scores():
    tkn = TokenizeSentences(SAMPLE)
    tkn.getTokens()
    tkn.tokenizeWords(SAMPLE)
    pre = Preprocess()
    pre.filterDocument(tkn)

    scorer = SentenceScoring()
    scorer.calculateScore(tkn, pre)
    scores = scorer.returnScore()

    assert len(scores) >= 1
    assert all(score >= 0 for score in scores.values())


def test_clustering_returns_summary():
    tkn = TokenizeSentences(SAMPLE)
    tkn.getTokens()
    tkn.tokenizeWords(SAMPLE)
    pre = Preprocess()
    pre.filterDocument(tkn)
    scorer = SentenceScoring()
    scorer.calculateScore(tkn, pre)
    scores = scorer.returnScore()

    clusters = MakeClusters()
    clusters.formClusters(scores)

    summary = clusters.chooseSentences(scores, top_n=3)
    assert summary.strip()
    assert len(summary.splitlines()) <= 3


@pytest.mark.parametrize("top_n", [1, 2, 3, 5])
def test_end_to_end_summarize(top_n):
    summary = summarize(SAMPLE, top_n=top_n)
    assert summary.strip()
    # Summary should be strictly shorter than the source.
    assert len(summary) < len(SAMPLE)
