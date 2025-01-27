from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from difflib import SequenceMatcher


class ParallelSimilarityCalculator:
    def __init__(self, max_workers=None, text_weight=0.4, structure_weight=0.6):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.text_weight = text_weight
        self.structure_weight = structure_weight

    def _node_similarity(self, node1: dict, node2: dict) -> float:
        """Node similarity calculation"""
        if not node1 or not node2:
            return 0.0
        if node1["type"] != node2["type"]:
            return 0.0

        text_sim = 1.0
        if node1["text"] != "<FILTERED>":
            text_sim = SequenceMatcher(None, node1["text"], node2["text"]).ratio()

        child_sim = self._children_similarity(node1["children"], node2["children"])
        return self.text_weight * text_sim + self.structure_weight * child_sim

    def _children_similarity(self, children1: list, children2: list) -> float:
        """Child node similarity calculation"""
        m, n = len(children1), len(children2)
        if m == 0 and n == 0:
            return 1.0
        if m == 0 or n == 0:
            return 0.0

        dp = [[0.0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                sim = self._node_similarity(children1[i - 1], children2[j - 1])
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1] + sim)

        return dp[m][n] / max(m, n) if max(m, n) > 0 else 0.0

    def compare_batch(self, ast_pairs):
        """Batch comparison with multithreading"""
        futures = {}
        with tqdm(total=len(ast_pairs), desc="Comparing files") as pbar:
            for (f1, ast1), (f2, ast2) in ast_pairs:
                future = self.executor.submit(self._node_similarity, ast1, ast2)
                futures[future] = (f1, f2)
                pbar.update(1)

            results = {}
            for future in as_completed(futures):
                f1, f2 = futures[future]
                results[(f1, f2)] = future.result()
        return results
