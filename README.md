# 📝 Text Summarizer

**An extractive NLP summarizer that ranks sentences by word frequency and proper-noun salience, then K-Means clusters them to pick the most important few.**

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![NLTK](https://img.shields.io/badge/nltk-3.8%2B-green)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-academic--project-lightgrey)

---

## 🎯 Problem Statement

The volume of text being produced every day — news articles, reports, blogs, research papers — has grown far faster than the time people have to read it. Skimming headlines is unreliable; reading every word is impossible. A tool that can compress a long document into a few representative sentences would let readers triage what's worth their full attention.

That is the problem this project addresses: **given a single document — either a text file or a web page — return a short summary built only from sentences that already appear in the source.**

## 💡 Solution

A four-module Python pipeline:

1. **Pre-process** the input with NLTK: tokenise into sentences, tokenise into words, strip stopwords, stem with the Porter stemmer, build a word-frequency table.
2. **Score** every sentence by summing the frequencies of its stemmed words, plus a bonus for proper-noun density (counts of `NNP` / `NNPS` POS tags).
3. **Cluster** the sentence scores with 1-D K-Means (k=2). The high-scoring cluster contains the candidate summary sentences.
4. **Choose** the top three sentences from the high-scoring cluster and return them as the summary. A PDF can be exported using FPDF.

The whole pipeline runs on a single machine in under a second per article. It is purely extractive — no neural network, no generation.

## ✨ Features

- 📄 Summarize a local text file
- 🌐 Summarize an HTML article straight from a URL (BeautifulSoup pulls the `<p>` tags)
- 🖥️ Original Tkinter GUI with checkboxes for input type and a "Download Summary" PDF button
- ⌨️ Headless CLI (`python main.py --file ...`) for scripting and tests
- 🧪 Pytest smoke tests covering every module
- 🧱 Clean four-module architecture matching the original report (Section 6.4)

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.9+ |
| NLP | NLTK (`punkt`, `stopwords`, `PorterStemmer`, `averaged_perceptron_tagger`) |
| HTML scraping | BeautifulSoup4, urllib |
| PDF export | fpdf2 |
| GUI | Tkinter |
| Tests | pytest |

## 🏗️ Architecture

```
text → PreProcess → Feature Extraction → K-Means (k=2) → top-N sentences → summary
```

See [`docs/architecture.md`](docs/architecture.md) for the full diagram, the per-module responsibilities, and the two bugs from the original report that were corrected.

## 🚀 How to Run

```bash
# 1. Clone and enter the repo
git clone https://github.com/<your-username>/text-summarizer.git
cd text-summarizer

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Summarize the bundled sample
python main.py --file data/sample.txt

# 5. Summarize a Wikipedia article
python main.py --url https://en.wikipedia.org/wiki/Natural_language_processing

# 6. (Optional) Launch the original Tkinter GUI
python main.py --gui

# 7. (Optional) Run the tests
pytest
```

NLTK data (`punkt`, `stopwords`, `averaged_perceptron_tagger`) is downloaded automatically on first run.

### Programmatic API

```python
from src.summarizer import summarize, summarize_url

print(summarize(open("article.txt").read(), top_n=3))
print(summarize_url("https://example.com/article", top_n=5))
```

## 📊 Results

On the bundled `data/sample.txt` (a short NLP-themed passage, ~7 paragraphs), the pipeline reliably returns the three sentences that mention proper nouns + frequent stems — the lead sentences of the article. The exact summary is reproducible by running `python main.py --file data/sample.txt` after `pytest` passes.

> ⚠️ Honest caveat — extractive summarization quality is hard to measure without a reference summary corpus (ROUGE etc.). This repo doesn't include one, so the README does not quote ROUGE numbers. Running the tool on a few articles and inspecting the output by eye is the project's qualitative evaluation.

## 🎓 Academic Context

Built as part of the **B.Tech Computer Science and Engineering** undergraduate program at **ACE Engineering College** (affiliated to JNTU Hyderabad), 2022.

This repository is a **reconstruction and documentation pass** of the original four-module project: the module split (Interface / PreProcess / Feature Extraction / Clustering), the algorithms (Porter stemming, NNP boost, K-Means with k=2, top-3 from cluster 1), and the Tkinter GUI all match the original report. The code has been refactored into a proper Python package, two clearly-broken loops in the original have been fixed (documented in `docs/architecture.md`), and a headless CLI and pytest suite have been added.

## 🔮 Future Improvements

If I were revisiting this project today, I would:

- Swap the hand-rolled frequency score for a real **TF-IDF** vectoriser over a small corpus, so common-but-uninformative words get downweighted properly.
- Replace the proper-noun boost with **TextRank** (a graph-based extractive method) for a more principled importance score.
- Add an **abstractive** mode using a small pre-trained transformer like `t5-small` or `bart-large-cnn`, gated behind a `--mode abstractive` flag.
- Evaluate against the **CNN/DailyMail** or **XSum** reference-summary corpus using ROUGE-1/2/L.
- Ship a small **FastAPI** service so the summarizer can be called over HTTP.
- Replace the Tkinter GUI with a **Streamlit** demo so it works without a desktop install.

## 👤 Author

**Chetana Varagantham**
B.Tech Computer Science & Engineering — ACE Engineering College, 2022
- 📧 [chetanavaragantham02@gmail.com](mailto:chetanavaragantham02@gmail.com)
- 💼 [LinkedIn](https://www.linkedin.com/in/chetanavaragantham
- 🐙 [GitHub](https://github.com/Chetanavaragantham

## 📝 License

[MIT](LICENSE)
