from pathlib import Path
import json


# --------------- Result Handler ---------------
class ResultHandler:
    @staticmethod
    def matrix(sim_dict: dict, files: list):
        """Output similarity matrix"""
        header = "Files\t" + "\t".join([Path(f).name for f in files])
        print(header)
        for f1 in files:
            row = [
                f"{sim_dict.get((f1, f2), sim_dict.get((f2, f1), 1.0 if f1 == f2 else 0)):.2f}"
                for f2 in files
            ]
            print(f"{Path(f1).name}\t" + "\t".join(row))

    @staticmethod
    def topn(sim_dict: dict, n: int = 5):
        """Output Top-N similar pairs"""
        sorted_pairs = sorted(
            [(k, v) for k, v in sim_dict.items() if k[0] != k[1]], key=lambda x: -x[1]
        )
        print(f"Top {n} Similar Pairs:")
        for (f1, f2), score in sorted_pairs[:n]:
            print(f"{score:.2%} | {Path(f1).name} <-> {Path(f2).name}")

    @staticmethod
    def json(sim_dict: dict):
        """Generate JSON report"""
        report = {
            "similarity_matrix": [
                {"file1": f1, "file2": f2, "score": round(score, 4)}
                for (f1, f2), score in sim_dict.items()
            ]
        }
        print(json.dumps(report, indent=2))
