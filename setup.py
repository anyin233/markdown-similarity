from distutils.core import setup
from Cython.Build import cythonize
import numpy as np
from distutils.core import Extension
import platform

# Detect platform and architecture
system = platform.system()
machine = platform.machine()

# Set SIMD flags based on architecture
if machine in ["x86_64", "AMD64"]:
    simd_flags = ["-march=native", "-mfma", "-msse4.2", "-mavx2"]
elif machine.startswith("arm64") or machine.startswith("aarch64"):
    simd_flags = ["-march=native", "-mcpu=native"]
else:
    simd_flags = ["-march=native"]  # fallback

extensions = [
    Extension(
        "lib.ast_processor",
        ["lib/ast_processor.pyx"],
        extra_compile_args=simd_flags,
        include_dirs=[np.get_include()],
    ),
    Extension(
        "lib.similarity_calculator",
        ["lib/similarity_calculator.pyx"],
        extra_compile_args=simd_flags,
        include_dirs=[np.get_include()],
    ),
    Extension(
        "lib.result_handler",
        ["lib/result_handler.pyx"],
        extra_compile_args=simd_flags,
        include_dirs=[np.get_include()],
    ),
]

setup(
    name="Markdown Compare",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
        },
        annotate=True,
    ),
    requires=["Cython", "tree_sitter", "tqdm"],
)
