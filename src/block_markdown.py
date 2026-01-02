from enum import Enum
from htmlnode import ParentNode, LeafNode
from textnode import text_node_to_html_node, TextNode, TextType
from inline_markdown import text_to_textnodes


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    """
    Split markdown text into blocks separated by blank lines.
    
    Args:
        markdown: Raw markdown string representing a full document
    
    Returns:
        List of block strings with leading/trailing whitespace stripped
    """
    # Split by double newline (blank line)
    blocks = markdown.split("\n\n")
    
    # Strip whitespace from each block and filter out empty blocks
    blocks = [block.strip() for block in blocks]
    blocks = [block for block in blocks if block]
    
    return blocks


def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    
    Args:
        block: A single block of markdown text (already stripped of leading/trailing whitespace)
    
    Returns:
        BlockType enum representing the type of block
    """
    lines = block.split("\n")
    
    # Check for heading: starts with 1-6 # characters followed by a space
    if block.startswith("#"):
        # Count leading # characters
        hash_count = 0
        for char in block:
            if char == "#":
                hash_count += 1
            else:
                break
        # Must be 1-6 # characters followed by a space
        if 1 <= hash_count <= 6 and len(block) > hash_count and block[hash_count] == " ":
            return BlockType.HEADING
    
    # Check for code block: starts with 3 backticks and ends with 3 backticks
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    # Check for quote: every line starts with >
    non_empty_lines = [line for line in lines if line.strip()]
    if non_empty_lines and all(line.startswith(">") for line in non_empty_lines):
        return BlockType.QUOTE
    
    # Check for unordered list: every line starts with - followed by a space
    if non_empty_lines and all(line.strip().startswith("- ") for line in non_empty_lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list: every line starts with number. followed by a space
    # Numbers must start at 1 and increment
    if non_empty_lines:
        is_ordered_list = True
        expected_number = 1
        for line in non_empty_lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Check if line starts with number. followed by space
            if not stripped[0].isdigit():
                is_ordered_list = False
                break
            # Extract the number
            number_str = ""
            i = 0
            while i < len(stripped) and stripped[i].isdigit():
                number_str += stripped[i]
                i += 1
            if not number_str or i >= len(stripped) or stripped[i] != "." or (i + 1 < len(stripped) and stripped[i + 1] != " "):
                is_ordered_list = False
                break
            # Check if number matches expected
            try:
                number = int(number_str)
                if number != expected_number:
                    is_ordered_list = False
                    break
                expected_number += 1
            except ValueError:
                is_ordered_list = False
                break
        if is_ordered_list:
            return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    """
    Convert text with inline markdown to a list of HTMLNode children.
    
    Args:
        text: Text string that may contain inline markdown
    
    Returns:
        List of HTMLNode objects representing the inline markdown
    """
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        children.append(text_node_to_html_node(text_node))
    return children


def heading_to_html_node(block):
    """
    Convert a heading block to an HTMLNode.
    
    Args:
        block: Heading block text (e.g., "# Heading" or "## Heading")
    
    Returns:
        ParentNode with h1-h6 tag containing inline markdown children
    """
    # Count leading # characters to determine heading level
    hash_count = 0
    for char in block:
        if char == "#":
            hash_count += 1
        else:
            break
    
    # Extract heading text (skip # characters and space)
    heading_text = block[hash_count + 1:].strip()
    
    # Create heading node with inline markdown children
    children = text_to_children(heading_text)
    return ParentNode(f"h{hash_count}", children)


def paragraph_to_html_node(block):
    """
    Convert a paragraph block to an HTMLNode.
    
    Args:
        block: Paragraph block text
    
    Returns:
        ParentNode with p tag containing inline markdown children
    """
    # Replace newlines with spaces for paragraphs
    paragraph_text = block.replace("\n", " ")
    children = text_to_children(paragraph_text)
    return ParentNode("p", children)


def code_to_html_node(block):
    """
    Convert a code block to an HTMLNode.
    Code blocks don't parse inline markdown.
    
    Args:
        block: Code block text (with ``` delimiters)
    
    Returns:
        ParentNode with pre tag containing code LeafNode
    """
    # Remove the opening and closing ```
    # Find the first newline after opening ```
    start_idx = block.find("\n")
    if start_idx == -1:
        # Single line code block
        code_text = block[3:-3]  # Remove ``` from start and end
    else:
        # Multi-line code block
        code_text = block[start_idx + 1:-3]  # Remove opening ``` and newline, closing ```
    
    # Create code node without inline markdown parsing
    code_node = LeafNode("code", code_text)
    return ParentNode("pre", [code_node])


def quote_to_html_node(block):
    """
    Convert a quote block to an HTMLNode.
    
    Args:
        block: Quote block text (each line starts with >)
    
    Returns:
        ParentNode with blockquote tag containing inline markdown children
    """
    lines = block.split("\n")
    # Remove > from start of each line and join with spaces (like paragraphs)
    quote_lines = []
    for line in lines:
        if line.startswith(">"):
            quote_lines.append(line[1:].strip())
        else:
            quote_lines.append(line.strip())
    
    quote_text = " ".join(quote_lines)
    children = text_to_children(quote_text)
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block):
    """
    Convert an unordered list block to an HTMLNode.
    
    Args:
        block: Unordered list block text (each line starts with - )
    
    Returns:
        ParentNode with ul tag containing li children
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            # Remove "- " prefix and create list item
            item_text = stripped[2:]
            item_children = text_to_children(item_text)
            list_items.append(ParentNode("li", item_children))
    
    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block):
    """
    Convert an ordered list block to an HTMLNode.
    
    Args:
        block: Ordered list block text (each line starts with number. )
    
    Returns:
        ParentNode with ol tag containing li children
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        stripped = line.strip()
        if stripped and stripped[0].isdigit():
            # Find the dot and space after the number
            i = 0
            while i < len(stripped) and stripped[i].isdigit():
                i += 1
            if i < len(stripped) and stripped[i] == ".":
                # Remove number. prefix and create list item
                item_text = stripped[i + 1:].strip()
                item_children = text_to_children(item_text)
                list_items.append(ParentNode("li", item_children))
    
    return ParentNode("ol", list_items)


def markdown_to_html_node(markdown):
    """
    Convert a full markdown document into a single parent HTMLNode.
    
    Args:
        markdown: Raw markdown string representing a full document
    
    Returns:
        ParentNode (div) containing all block nodes as children
    """
    # Split markdown into blocks
    blocks = markdown_to_blocks(markdown)
    
    # Convert each block to HTMLNode
    block_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.HEADING:
            block_nodes.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            block_nodes.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            block_nodes.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            block_nodes.append(unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            block_nodes.append(ordered_list_to_html_node(block))
        else:  # PARAGRAPH
            block_nodes.append(paragraph_to_html_node(block))
    
    # Wrap all blocks in a div
    return ParentNode("div", block_nodes)

