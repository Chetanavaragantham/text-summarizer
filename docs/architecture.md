# Architecture

## System diagram

```
                     ┌────────────────────────────┐
                     │  Input: text file or URL   │
                     └─────────────┬──────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │  Interface Module │   (src/gui.py + main.py)
                         │  (Tkinter / CLI)  │
                         └─────────┬─────────┘
                                   │  raw string
                                   ▼
                         ┌─────────────────────┐
                         │ PreProcess Module   │   (src/preprocess_module.py)
                         │ • TokenizeSentences │
                         │ • Preprocess        │   → word-frequency table
                         └─────────┬───────────┘
                                   ▼
                       ┌───────────────────────┐
                       │ Feature Extraction    │   (src/feature_extraction_module.py)
                       │ • SentenceScoring     │   freq score + NNP/NNPS boost
                       └─────────┬─────────────┘
                                 ▼
                       ┌──────────────────────┐
                       │ Clustering Module    │   (src/cluster_module.py)
                       │ K-Means, k=2         │   pick top-N from cluster 1
                       └─────────┬────────────┘
                                 ▼
                       ┌──────────────────────┐
                       │ Summary string       │
                       │ (PDF via FPDF, GUI)  │
                       └──────────────────────┘
```

## Module responsibilities

### PreProcess Module
- **`TokenizeSentences`** wraps NLTK's `sent_tokenize` and `word_tokenize`. The
  same instance carries both `.sentences` and `.words` so downstream modules
  don't re-tokenise.
- **`Preprocess`** removes stopwords and a small symbol set, then applies the
  Porter stemmer to each remaining token and counts frequencies. The resulting
  `.frequency_table` is the only data structure the next module needs.

### Feature Extraction Module
- **`SentenceScoring.calculateScore`** sums the stemmed-word frequencies that
  appear inside each sentence, then divides by a running counter the original
  report calls `tfidf`. The counter is *not* a true TF-IDF score — it's a
  per-document normalisation that softens the bias toward long sentences.
- After the frequency pass, `calculateScore` walks every sentence again with
  `nltk.pos_tag`, counts `NNP` and `NNPS` tags, and adds the local
  proper-noun ratio as a bonus. Articles with named entities (people, places,
  organisations) tend to surface key sentences this way.

### Clustering Module
- **`MakeClusters.formClusters`** runs a 1-D K-Means with k=2 over the
  sentence scores. Centroid 1 starts at the maximum score, centroid 2 at the
  minimum. Iteration stops when the sum of squared distances stops improving
  (or after 50 passes, whichever comes first).
- **`MakeClusters.chooseSentences`** returns the top-N sentences from the
  high-scoring cluster. N defaults to 3, matching the report.

## Design decisions (and a couple of corrected bugs)

### Why two-cluster K-Means rather than a percentile cut-off?
Choosing the top *k* sentences directly requires picking *k* up-front. K-Means
adapts to the score distribution — if 12 of 20 sentences are roughly equally
important, all 12 land in cluster 1 and `chooseSentences` still applies its
own top-3 cap. The score-cutoff approach throws away the natural break.

### Why proper-noun boost rather than full TF-IDF?
A genuine TF-IDF score would need an external document corpus to compute
inverse-document-frequency. The original undergraduate project had to run on
a single document, so it leaned on POS tagging instead. Proper nouns are a
cheap, document-local proxy for "this sentence names something the article
is actually about."

### Bugs corrected from the original report
1. **K-Means termination** — the original report's loop guard
   (`while sserror <= psserror`) is unreachable on iteration 1 because both
   variables start at 0. The fix uses an `abs(prev - curr) < tol` rule with
   an iteration cap (50).
2. **Per-sentence proper-noun counter** — the original kept `sncount`
   accumulating across the outer sentence loop, so every sentence got the
   running cumulative total. The fix resets the counter per-sentence so each
   sentence is scored on its own NNP/NNPS ratio.

Both fixes preserve the algorithm's intent; they remove silent failures, not
correct outputs.

## Limitations honestly stated

- Extractive only. Cannot rephrase or compress.
- Sentence-level scoring; no awareness of paragraph or discourse structure.
- English only (Porter stemmer and the NLTK stopword list).
- Top-N is a fixed budget — no length-aware summary.
- POS-tagger dependence makes cold runs slow (≈1–2 s on a short article).
