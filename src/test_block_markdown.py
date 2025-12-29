import unittest
from block_markdown import markdown_to_blocks, block_to_block_type, BlockType


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_single_block(self):
        md = "This is a single block of text"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a single block of text"])

    def test_multiple_blocks(self):
        md = """# Heading

Paragraph text

- List item 1
- List item 2
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Heading",
                "Paragraph text",
                "- List item 1\n- List item 2",
            ],
        )

    def test_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_only_whitespace(self):
        md = "   \n\n   \n\n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_multiple_blank_lines(self):
        md = """Block 1


Block 2


Block 3"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])

    def test_leading_trailing_whitespace(self):
        md = """   Block 1   

   Block 2   

   Block 3   """
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])

    def test_block_with_newlines(self):
        md = """Block 1 line 1
Block 1 line 2
Block 1 line 3

Block 2 line 1
Block 2 line 2"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "Block 1 line 1\nBlock 1 line 2\nBlock 1 line 3",
                "Block 2 line 1\nBlock 2 line 2",
            ],
        )

    def test_heading_and_paragraph(self):
        md = """# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it."""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
            ],
        )

    def test_list_block(self):
        md = """- This is the first list item in a list block
- This is a list item
- This is another list item"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
        )

    def test_three_blocks_example(self):
        md = """# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        block = "This is a regular paragraph of text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_multiple_lines(self):
        block = "This is a paragraph\nwith multiple lines\nof text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_h1(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h2(self):
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h3(self):
        block = "### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h4(self):
        block = "#### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h5(self):
        block = "##### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_h6(self):
        block = "###### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_not_seven_hashes(self):
        block = "####### This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_no_space_after_hash(self):
        block = "#This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block(self):
        block = "```\ncode here\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_with_content(self):
        block = "```python\ndef hello():\n    print('world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_single_line(self):
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_not_closed(self):
        block = "```\ncode here"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block_not_opened(self):
        block = "code here\n```"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_multiple_lines(self):
        block = "> This is a quote\n> with multiple lines\n> of quoted text"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_with_empty_line(self):
        block = "> Line 1\n> \n> Line 2"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_not_all_lines(self):
        block = "> Line 1\nNot a quote line"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_single_item(self):
        block = "- List item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple_items(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_with_space(self):
        block = "- Item 1\n- Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_no_space_after_dash(self):
        block = "-Item 1\n-Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_not_all_lines(self):
        block = "- Item 1\nRegular text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_single_item(self):
        block = "1. First item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_multiple_items(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_sequential_numbers(self):
        block = "1. Item\n2. Item\n3. Item\n4. Item\n5. Item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_wrong_starting_number(self):
        block = "2. First item\n3. Second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_non_sequential(self):
        block = "1. First item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_no_space_after_dot(self):
        block = "1.First item\n2.Second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_no_dot(self):
        block = "1 First item\n2 Second item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_not_all_lines(self):
        block = "1. First item\nRegular text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_double_digit(self):
        block = "1. Item\n2. Item\n3. Item\n4. Item\n5. Item\n6. Item\n7. Item\n8. Item\n9. Item\n10. Item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_paragraph_with_hash_not_heading(self):
        block = "This has a # symbol but is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_dash_not_list(self):
        block = "This has a - symbol but is not a list"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_number_not_list(self):
        block = "This has a 1 symbol but is not a list"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_empty_block(self):
        block = ""
        # Empty block should default to paragraph
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block_with_language(self):
        block = "```javascript\nconsole.log('hello');\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_with_indentation(self):
        block = "> Quote line 1\n> Quote line 2"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)


if __name__ == "__main__":
    unittest.main()

