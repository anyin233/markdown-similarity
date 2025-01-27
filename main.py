"""
Multi-threaded Markdown similarity comparison tool based on tree-sitter (with progress bar)
Dependencies: pip install tree-sitter tree-sitter-markdown tqdm
Usage: python md_compare.py <files.md> ... [output_format]
"""

import sys
import itertools
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from lib import ASTProcessor, ParallelSimilarityCalculator, ResultHandler


def parse_ast_parallel(file):
    return file, ASTProcessor.parse(file)


def main():
    if len(sys.argv) < 3:
        print("Usage: python md_compare.py <file1.md> ... [matrix|topn|json]")
        sys.exit(1)

    files = sys.argv[1:-1]
    output_format = sys.argv[-1]

    # File validation and filtering
    valid_files = []
    for f in files:
        path = Path(f)
        if not path.exists():
            print(f"Error: File {path} not found")
            sys.exit(1)
        if path.suffix.lower() == ".md":
            valid_files.append(str(path.resolve()))

    # Batch parse AST (main thread)
    print("Parsing ASTs...")
    # ast_cache = {f: ASTProcessor.parse(f) for f in valid_files}

    with ThreadPoolExecutor(max_workers=8) as executor:
        ast_results = executor.map(parse_ast_parallel, valid_files)
        ast_cache = dict(ast_results)

    # Generate comparison pairs
    pairs = list(itertools.combinations(valid_files, 2))
    ast_pairs = [((f1, ast_cache[f1]), (f2, ast_cache[f2])) for f1, f2 in pairs]

    # Multithreaded comparison
    print("Calculating similarities...")
    calculator = ParallelSimilarityCalculator(max_workers=8)
    sim_dict = calculator.compare_batch(ast_pairs)

    # Output results
    handler_map = {
        "matrix": lambda: ResultHandler.matrix(sim_dict, valid_files),
        "topn": lambda: ResultHandler.topn(sim_dict),
        "json": lambda: ResultHandler.json(sim_dict),
    }
    handler_map.get(output_format, lambda: print("Invalid output format"))()
    # ResultHandler().handle(output_format, sim_dict, valid_files)


if __name__ == "__main__":
    main()
