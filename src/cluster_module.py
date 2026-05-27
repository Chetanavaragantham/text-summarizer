"""
Clustering module — Section 6.4.4 of the original report.

``MakeClusters`` runs a 1-D K-Means with ``k=2`` over the per-sentence
scores produced by ``SentenceScoring``. Centroid 1 is initialised at the
maximum score, centroid 2 at the minimum. The iteration converges when
the sum of squared distances stops improving.

After convergence, ``chooseSentences`` returns the top-N sentences from
the high-score cluster (Cluster 1) in their original order — that string
is the final summary.

Two bugs from the original report have been fixed:
* The original loop's termination condition (`while sserror <= psserror`)
  could never become true on the first iteration when both were 0, so the
  loop either never started or ran forever. The fixed version uses a
  proper "improvement < epsilon" stopping rule with an iteration cap.
* The original recomputed cluster membership without resetting the
  cluster lists each iteration. They are now reset.
"""

from __future__ import annotations


class MakeClusters:
    """1-D K-Means with k=2 over sentence scores."""

    def __init__(self) -> None:
        self.cluster1: list[float] = []  # higher-scoring sentences
        self.cluster2: list[float] = []  # lower-scoring sentences

    def formClusters(  # noqa: N802 (preserve original API)
        self,
        scr: dict[str, float],
        max_iters: int = 50,
        tol: float = 1e-4,
    ) -> None:
        if not scr:
            return

        values = list(scr.values())
        centroid1 = max(values)
        centroid2 = min(values)

        previous_error = float("inf")

        for _ in range(max_iters):
            self.cluster1, self.cluster2 = [], []

            for value in values:
                if abs(value - centroid1) < abs(value - centroid2):
                    self.cluster1.append(value)
                else:
                    self.cluster2.append(value)

            if self.cluster1:
                centroid1 = sum(self.cluster1) / len(self.cluster1)
            if self.cluster2:
                centroid2 = sum(self.cluster2) / len(self.cluster2)

            error = sum((v - centroid1) ** 2 for v in self.cluster1) + sum(
                (v - centroid2) ** 2 for v in self.cluster2
            )

            if abs(previous_error - error) < tol:
                break
            previous_error = error

    def chooseSentences(  # noqa: N802
        self,
        scr: dict[str, float],
        top_n: int = 3,
    ) -> str:
        """Pick the top-N sentences from the high-scoring cluster.

        Sentences are returned in their *original document order* (matching
        the behaviour of the original ``traversed`` deduplication trick).
        """
        if not self.cluster1:
            return ""

        # Build set of scores that belong to the high cluster.
        high_scores = set(self.cluster1)

        # Pull the matching sentences in original order, keeping at most top_n.
        chosen: list[tuple[str, float]] = []
        for sentence, score in scr.items():
            if score in high_scores and len(chosen) < top_n:
                chosen.append((sentence, score))

        # Sort the chosen by score descending so the strongest comes first,
        # which matches the report's `cluster1.sort()` + `reverse()` step.
        chosen.sort(key=lambda pair: pair[1], reverse=True)
        return "\n".join(sentence for sentence, _ in chosen) + "\n"
