import os
import sys
import shutil
from pathlib import Path
from block_markdown import markdown_to_html_node


def extract_title(markdown: str) -> str:
    """
    Extract the h1 header from markdown text.
    
    Args:
        markdown: The markdown content to search through
        
    Returns:
        The text content of the h1 header (without the # and whitespace)
        
    Raises:
        ValueError: If no h1 header is found
    """
    lines = markdown.split('\n')
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('# '):
            # Remove "# " and any additional whitespace
            title = stripped_line[2:].strip()
            if title:  # Ensure title is not empty
                return title
    
    raise ValueError("No h1 header found in markdown content")


def copy_directory_contents(src_dir: str, dest_dir: str):
    """
    Recursively copy all contents from source directory to destination directory.
    First deletes all contents of destination directory to ensure a clean copy.
    
    Args:
        src_dir: Source directory path
        dest_dir: Destination directory path
    """
    # Convert to Path objects for easier manipulation
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    # Check if source directory exists
    if not src_path.exists():
        raise ValueError(f"Source directory does not exist: {src_dir}")
    
    if not src_path.is_dir():
        raise ValueError(f"Source path is not a directory: {src_dir}")
    
    # Delete destination directory contents if it exists
    if dest_path.exists():
        print(f"Deleting contents of {dest_dir}...")
        shutil.rmtree(dest_path)
    
    # Create destination directory
    dest_path.mkdir(parents=True, exist_ok=True)
    print(f"Created destination directory: {dest_dir}")
    
    # Recursively copy all files and directories
    def copy_recursive(src: Path, dest: Path):
        """Helper function to recursively copy files and directories."""
        for item in src.iterdir():
            src_item = src / item.name
            dest_item = dest / item.name
            
            if src_item.is_file():
                # Copy file
                shutil.copy2(src_item, dest_item)
                print(f"Copied file: {dest_item}")
            elif src_item.is_dir():
                # Create directory and recurse
                dest_item.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {dest_item}")
                copy_recursive(src_item, dest_item)
    
    # Start recursive copy
    copy_recursive(src_path, dest_path)
    print(f"Successfully copied all contents from {src_dir} to {dest_dir}")


def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str = "/"):
    """
    Generate an HTML page from markdown using a template.
    
    Args:
        from_path: Path to the markdown file
        template_path: Path to the HTML template file  
        dest_path: Path where the generated HTML file should be written
        basepath: Base path for the site (e.g., "/" or "/REPO_NAME/")
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown file
    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Read template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract title from markdown
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    # Replace href="/ and src="/ with basepath
    # Ensure basepath ends with / for proper replacement
    if not basepath.endswith("/"):
        basepath = basepath + "/"
    
    # Replace href="/ with href="{basepath}
    final_html = final_html.replace('href="/', f'href="{basepath}')
    # Replace src="/ with src="{basepath}
    final_html = final_html.replace('src="/', f'src="{basepath}')
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
    
    # Write final HTML to destination
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"Page generated successfully at {dest_path}")


def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str = "/"):
    """
    Recursively generate HTML pages from all markdown files in the content directory.
    
    Args:
        dir_path_content: Path to the content directory containing markdown files
        template_path: Path to the HTML template file
        dest_dir_path: Path to the destination directory where HTML files will be written
        basepath: Base path for the site (e.g., "/" or "/REPO_NAME/")
    """
    content_path = Path(dir_path_content)
    template_path_obj = Path(template_path)
    dest_path = Path(dest_dir_path)
    
    # Verify content directory exists
    if not content_path.exists():
        raise ValueError(f"Content directory does not exist: {dir_path_content}")
    
    if not content_path.is_dir():
        raise ValueError(f"Content path is not a directory: {dir_path_content}")
    
    # Verify template exists
    if not template_path_obj.exists():
        raise ValueError(f"Template file does not exist: {template_path}")
    
    # Read template once (it's the same for all pages)
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Ensure basepath ends with / for proper replacement
    if not basepath.endswith("/"):
        basepath = basepath + "/"
    
    # Recursively walk through content directory
    def process_directory(current_content_dir: Path, current_dest_dir: Path):
        """Recursively process directories and generate HTML from markdown files."""
        # Ensure destination directory exists
        current_dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Process all items in current directory
        for item in current_content_dir.iterdir():
            content_item = current_content_dir / item.name
            
            if content_item.is_file() and content_item.suffix == '.md':
                # Found a markdown file, generate HTML
                # Replace .md extension with .html
                dest_file = current_dest_dir / (content_item.stem + '.html')
                
                # Read markdown file
                with open(content_item, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                # Convert markdown to HTML
                html_node = markdown_to_html_node(markdown_content)
                html_content = html_node.to_html()
                
                # Extract title from markdown
                title = extract_title(markdown_content)
                
                # Replace placeholders in template
                final_html = template_content.replace("{{ Title }}", title)
                final_html = final_html.replace("{{ Content }}", html_content)
                
                # Replace href="/ and src="/ with basepath
                final_html = final_html.replace('href="/', f'href="{basepath}')
                final_html = final_html.replace('src="/', f'src="{basepath}')
                
                # Write final HTML to destination
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(final_html)
                
                print(f"Generated: {dest_file}")
                
            elif content_item.is_dir():
                # Found a directory, recurse into it
                dest_subdir = current_dest_dir / item.name
                process_directory(content_item, dest_subdir)
    
    # Start recursive processing
    process_directory(content_path, dest_path)
    print(f"Successfully generated all pages from {dir_path_content} to {dest_dir_path}")


def main():
    # Get basepath from CLI argument, default to "/"
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    print(f"Using basepath: {basepath}")
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Use docs directory for output (GitHub Pages)
    output_dir = project_root / "docs"
    if output_dir.exists():
        print(f"Deleting docs directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Copy static files to docs directory
    static_dir = project_root / "static"
    print("Starting static file copy...")
    copy_directory_contents(str(static_dir), str(output_dir))
    print("Static file copy complete!")
    
    # Generate all pages recursively from markdown files
    content_dir = project_root / "content"
    template_path = project_root / "template.html"
    
    print("Starting page generation...")
    generate_pages_recursive(str(content_dir), str(template_path), str(output_dir), basepath)
    print("Site generation complete!")


if __name__ == "__main__":
    main()
