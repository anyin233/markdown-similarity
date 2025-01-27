# cython: language_level=3
cimport cython
from libc.stdlib cimport malloc, free
from tree_sitter import Language, Parser
import tree_sitter_markdown as tsmd
from functools import lru_cache

MARKDOWN_LANG = Language(tsmd.language())
parser = Parser(MARKDOWN_LANG)

filtered_blocks = ["code_block", "html_block", "link", "image"]

cdef dict _normalize_node(object node):
    """Internal normalization function for Cython"""
    cdef list filtered_types = ['link', 'image', 'code_block', 'html_block']
    cdef str text
    cdef list children = []
    cdef object child
    
    if not node:
        return None
    
    if node.type in filtered_types:
        return {'type': node.type, 'text': '<FILTERED>', 'children': []}
    
    text = node.text.decode('utf-8').strip() if node.text else ''
    
    for child in node.children:
        if child.type in ['link_destination', 'link_title']:
            continue
        normalized = _normalize_node(child)
        if normalized:
            children.append(normalized)
    
    return {'type': node.type, 'text': text, 'children': children}

cdef class ASTProcessor:
    @staticmethod
    @lru_cache(maxsize=100)
    def parse(str file_path):
        """Parse file and generate normalized AST"""
        cdef bytes code
        with open(file_path, 'rb') as f:
            code = f.read()
        tree = parser.parse(code)
        return _normalize_node(tree.root_node)

    @staticmethod
    def normalize(object node):
        """Normalize node structure (calls internal Cython function)"""
        return _normalize_node(node)