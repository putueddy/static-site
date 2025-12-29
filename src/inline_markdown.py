from textnode import TextNode, TextType

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
