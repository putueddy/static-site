import re
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


def extract_markdown_images(text):
    """
    Extract markdown images from text.
    
    Args:
        text: Raw markdown text containing image syntax ![alt](url)
    
    Returns:
        List of tuples, each containing (alt_text, url)
    """
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    """
    Extract markdown links from text (excluding images).
    
    Args:
        text: Raw markdown text containing link syntax [anchor](url)
    
    Returns:
        List of tuples, each containing (anchor_text, url)
    """
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    """
    Split TextType.TEXT nodes that contain markdown images.
    
    Args:
        old_nodes: List of TextNode objects
    
    Returns:
        New list of TextNode objects with TEXT nodes split around images
    """
    new_nodes = []
    
    for node in old_nodes:
        # Only split TEXT type nodes, leave others as-is
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        # Extract images from the text
        images = extract_markdown_images(node.text)
        
        # If no images found, keep the node as-is
        if not images:
            new_nodes.append(node)
            continue
        
        # Process each image one at a time
        remaining_text = node.text
        for alt_text, url in images:
            # Construct the markdown syntax for this image
            image_markdown = f"![{alt_text}]({url})"
            
            # Split at the first occurrence of this image markdown
            sections = remaining_text.split(image_markdown, 1)
            
            # Add the text before the image (if not empty)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            # Add the image node
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            # Continue with the remaining text
            remaining_text = sections[1] if len(sections) > 1 else ""
        
        # Add any remaining text after the last image (if not empty)
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def split_nodes_link(old_nodes):
    """
    Split TextType.TEXT nodes that contain markdown links.
    
    Args:
        old_nodes: List of TextNode objects
    
    Returns:
        New list of TextNode objects with TEXT nodes split around links
    """
    new_nodes = []
    
    for node in old_nodes:
        # Only split TEXT type nodes, leave others as-is
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        # Extract links from the text
        links = extract_markdown_links(node.text)
        
        # If no links found, keep the node as-is
        if not links:
            new_nodes.append(node)
            continue
        
        # Process each link one at a time
        remaining_text = node.text
        for anchor_text, url in links:
            # Construct the markdown syntax for this link
            link_markdown = f"[{anchor_text}]({url})"
            
            # Split at the first occurrence of this link markdown
            sections = remaining_text.split(link_markdown, 1)
            
            # Add the text before the link (if not empty)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            # Add the link node
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            
            # Continue with the remaining text
            remaining_text = sections[1] if len(sections) > 1 else ""
        
        # Add any remaining text after the last link (if not empty)
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def text_to_textnodes(text):
    """
    Convert raw markdown text into a list of TextNode objects.
    
    Processes images, links, bold, italic, and code markdown syntax.
    
    Args:
        text: Raw markdown text string
    
    Returns:
        List of TextNode objects with appropriate types
    """
    # Start with a single TEXT node containing the entire text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Process in order: images, links, then delimiters (bold, italic, code)
    # Images and links are processed first because they're more complex
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes
