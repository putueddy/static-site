from enum import Enum
from htmlnode import LeafNode

class TextType(Enum):
    TEXT = "Text"
    BOLD = "Bold"
    ITALIC = "Italic"
    CODE = "Code"
    LINK = "Link"
    IMAGE = "Image"

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str = None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        if text_node.url is None:
            raise ValueError("Link TextNode must have a URL")
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        if text_node.url is None:
            raise ValueError("Image TextNode must have a URL")
        return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError(f"Unsupported text type: {text_node.text_type}")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Split TextType.TEXT nodes by a delimiter and convert delimited sections to the specified text_type.
    
    Args:
        old_nodes: List of TextNode objects
        delimiter: String delimiter to split by (e.g., "**", "_", "`")
        text_type: TextType to assign to delimited sections
    
    Returns:
        New list of TextNode objects with TEXT nodes split appropriately
    
    Raises:
        ValueError: If a matching closing delimiter is not found
    """
    new_nodes = []
    
    for node in old_nodes:
        # Only split TEXT type nodes, leave others as-is
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        # If text doesn't contain delimiter, just add it as-is
        if delimiter not in node.text:
            new_nodes.append(node)
            continue
        
        # Split by delimiter
        parts = node.text.split(delimiter)
        
        # If we have an even number of parts, there's an unmatched delimiter
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown: unmatched delimiter '{delimiter}'")
        
        # Create new nodes: even indices are TEXT, odd indices are the specified text_type
        for i, part in enumerate(parts):
            # Skip empty strings only at the very beginning or end
            if not part and (i == 0 or i == len(parts) - 1):
                continue
            if i % 2 == 0:
                # Even index: regular text
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # Odd index: delimited text
                new_nodes.append(TextNode(part, text_type))
    
    return new_nodes
