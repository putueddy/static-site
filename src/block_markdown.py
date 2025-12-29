from enum import Enum


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

