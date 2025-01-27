# cython: language_level=3
cimport cython
from pathlib import Path
import json

cdef list _get_sorted_pairs(dict sim_dict):
    """Cython 内部使用的排序函数"""
    cdef list pairs = []
    cdef tuple key
    cdef double value
    for key, value in sim_dict.items():
        if key[0] != key[1]:
            pairs.append((key, value))
    pairs.sort(key=lambda x: -x[1])  # 排序逻辑
    return pairs

cdef class ResultHandler:
    @staticmethod
    def matrix(dict sim_dict, list files):
        """输出相似性矩阵"""
        cdef str header = "Files\t" + "\t".join([Path(f).name for f in files])
        print(header)
        cdef str f1, f2
        cdef list row
        for f1 in files:
            row = []
            for f2 in files:
                if f1 == f2:
                    row.append("1.00")
                else:
                    score = sim_dict.get((f1, f2), sim_dict.get((f2, f1), 0.0))
                    row.append(f"{score:.2f}")
            print(f"{Path(f1).name}\t" + "\t".join(row))

    @staticmethod
    def topn(dict sim_dict, int n=5):
        """输出 Top-N 相似对"""
        cdef list sorted_pairs = _get_sorted_pairs(sim_dict)
        print(f"Top {n} Similar Pairs:")
        cdef tuple pair
        cdef double score
        for pair, score in sorted_pairs[:n]:
            print(f"{score:.2%} | {Path(pair[0]).name} <-> {Path(pair[1]).name}")

    @staticmethod
    def json(dict sim_dict):
        """生成 JSON 报告"""
        cdef list report = [
            {"file1": f1, "file2": f2, "score": round(score, 4)}
            for (f1, f2), score in sim_dict.items()
        ]
        print(json.dumps({"similarity_matrix": report}, indent=2))