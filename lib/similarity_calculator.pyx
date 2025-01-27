# cython: language_level=3
cimport cython
from cython.view cimport array as cvarray
from libc.math cimport fmax
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from difflib import SequenceMatcher
import numpy as np

cdef double jaccard_similarity(str text1, str text2):
    cdef set set1 = set(text1.split())
    cdef set set2 = set(text2.split())
    cdef int intersection = len(set1 & set2)
    cdef int union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

cdef class ParallelSimilarityCalculator:
    cdef readonly double text_weight
    cdef readonly double structure_weight
    cdef object executor
    cdef int max_workers  # Explicitly declare as int type

    def __init__(self, max_workers=None, double text_weight=0.4, double structure_weight=0.6):
        # Convert max_workers to a valid integer value
        if max_workers is None:
            self.max_workers = 0  # Default value for ThreadPoolExecutor
        else:
            self.max_workers = max_workers  # Ensure it is of int type

        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.text_weight = text_weight
        self.structure_weight = structure_weight

    cdef double _node_similarity(self, dict node1, dict node2):
        cdef double text_sim, child_sim
        cdef str node1_type = node1['type']
        cdef str node2_type = node2['type']
        cdef str node1_text = node1['text']
        cdef str node2_text = node2['text']
        cdef list node1_children = node1['children']
        cdef list node2_children = node2['children']

        if not node1 or not node2:
            return 0.0

        if node1_type != node2_type:
            return 0.0

        # text_sim = 1.0 if node1_text == '<FILTERED>' else SequenceMatcher(
        #   None, node1_text, node2_text).ratio()
        
        text_sim = 1.0 if node1_text == '<FILTERED>' else jaccard_similarity(
            node1_text, node2_text)

        child_sim = self._children_similarity(node1_children, node2_children)
        return self.text_weight * text_sim + self.structure_weight * child_sim

    cdef double _children_similarity(self, list children1, list children2):
        cdef int m = len(children1), n = len(children2)
        cdef double[:, :] dp
        cdef int i, j

        if m == 0 and n == 0:
            return 1.0
        if m == 0 or n == 0:
            return 0.0

        # Initialize the dynamic programming matrix using memoryview
        dp = cvarray(shape=(m + 1, n + 1), itemsize=sizeof(double), format="d")
        dp[:, :] = 0.0  # Initialize all values to 0.0

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                sim = self._node_similarity(children1[i - 1], children2[j - 1])
                dp[i][j] = fmax(fmax(dp[i - 1][j], dp[i][j - 1]), dp[i - 1][j - 1] + sim)

        return dp[m][n] / fmax(m, n)

    def compare_batch(self, ast_pairs):
        """Multithreaded batch comparison"""
        cdef dict futures = {}
        cdef str f1, f2
        cdef dict ast1, ast2
        cdef dict results = {}

        with tqdm(total=len(ast_pairs), desc="Comparing files") as pbar:
            for (f1, ast1), (f2, ast2) in ast_pairs:
                future = self.executor.submit(
                    self._node_similarity, ast1, ast2
                )
                futures[future] = (f1, f2)
                pbar.update(1)

            
            for future in as_completed(futures):
                f1, f2 = futures[future]
                results[(f1, f2)] = future.result()
        return results