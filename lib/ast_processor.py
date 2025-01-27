from tree_sitter import Language, Parser
import tree_sitter_markdown as tsmd

MARKDOWN_LANG = Language(tsmd.language())
parser = Parser(MARKDOWN_LANG)

filtered_blocks = ["code_block", "html_block", "link", "image"]


class ASTProcessor:
    @staticmethod
    def parse(file_path: str) -> dict:
        """Parse file and generate standardized AST"""
        with open(file_path, "rb") as f:
            code = f.read()
        tree = parser.parse(code)
        return ASTProcessor.normalize(tree.root_node)

    @staticmethod
    def normalize(node) -> dict:
        """Standardize node structure"""
        if not node:
            return None

        # Filter out code blocks and other content that does not need to be compared
        if node.type in filtered_blocks:
            return {"type": node.type, "text": "<FILTERED>", "children": []}

        text = node.text.decode("utf-8").strip() if node.text else ""
        children = []
        for child in node.children:
            normalized = ASTProcessor.normalize(child)
            if normalized:
                children.append(normalized)

        return {"type": node.type, "text": text, "children": children}
