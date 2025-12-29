import unittest
from textnode import TextNode, TextType
from inline_markdown import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_bold_delimiter(self):
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bolded phrase", TextType.BOLD),
            TextNode(" in the middle", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_italic_delimiter(self):
        node = TextNode("This is text with an _italic phrase_ in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("italic phrase", TextType.ITALIC),
            TextNode(" in the middle", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_no_delimiter(self):
        node = TextNode("This is just plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("This is just plain text", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_delimiter_at_start(self):
        node = TextNode("**bold text** at start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("bold text", TextType.BOLD),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delimiter_at_end(self):
        node = TextNode("text at end `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("text at end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_only_delimited_text(self):
        node = TextNode("**only bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [TextNode("only bold", TextType.BOLD)]
        self.assertEqual(new_nodes, expected)

    def test_multiple_delimiters(self):
        node = TextNode("text `code1` more `code2` end", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("text ", TextType.TEXT),
            TextNode("code1", TextType.CODE),
            TextNode(" more ", TextType.TEXT),
            TextNode("code2", TextType.CODE),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_unmatched_delimiter(self):
        node = TextNode("text with `unmatched code", TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("unmatched delimiter", str(context.exception).lower())

    def test_unmatched_delimiter_bold(self):
        node = TextNode("text with **unmatched bold", TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertIn("unmatched delimiter", str(context.exception).lower())

    def test_non_text_node_preserved(self):
        node1 = TextNode("This is text with `code`", TextType.TEXT)
        node2 = TextNode("This is bold", TextType.BOLD)
        node3 = TextNode("More text with `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node1, node2, node3], "`", TextType.CODE)
        expected = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode("This is bold", TextType.BOLD),
            TextNode("More text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_empty_string_between_delimiters(self):
        # Test with 2 backticks for an empty code block in the middle
        node = TextNode("text `` more", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("text ", TextType.TEXT),
            TextNode("", TextType.CODE),
            TextNode(" more", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_empty_string_at_start(self):
        # Test with delimiters at start and end - empty strings at edges are skipped
        # Using 2 backticks: ``code`` splits to ["", "code", ""]
        node = TextNode("`code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        # Empty strings at start and end are skipped, so we only get the code part
        expected = [TextNode("code", TextType.CODE)]
        self.assertEqual(new_nodes, expected)

    def test_multiple_non_text_nodes(self):
        node1 = TextNode("Bold text", TextType.BOLD)
        node2 = TextNode("Italic text", TextType.ITALIC)
        node3 = TextNode("Code text", TextType.CODE)
        new_nodes = split_nodes_delimiter([node1, node2, node3], "`", TextType.CODE)
        expected = [node1, node2, node3]
        self.assertEqual(new_nodes, expected)

    def test_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        expected = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")
        ]
        self.assertListEqual(expected, matches)

    def test_extract_no_images(self):
        matches = extract_markdown_images("This is just plain text")
        self.assertListEqual([], matches)

    def test_extract_image_at_start(self):
        matches = extract_markdown_images("![start](https://example.com/image.png) and text")
        self.assertListEqual([("start", "https://example.com/image.png")], matches)

    def test_extract_image_at_end(self):
        matches = extract_markdown_images("text and ![end](https://example.com/image.png)")
        self.assertListEqual([("end", "https://example.com/image.png")], matches)

    def test_extract_image_with_empty_alt(self):
        matches = extract_markdown_images("![ ](https://example.com/image.png)")
        self.assertListEqual([(" ", "https://example.com/image.png")], matches)

    def test_extract_image_with_complex_url(self):
        matches = extract_markdown_images("![alt](https://example.com/path/to/image.png?param=value)")
        self.assertListEqual([("alt", "https://example.com/path/to/image.png?param=value")], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        expected = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev")
        ]
        self.assertListEqual(expected, matches)

    def test_extract_no_links(self):
        matches = extract_markdown_links("This is just plain text")
        self.assertListEqual([], matches)

    def test_extract_link_at_start(self):
        matches = extract_markdown_links("[start](https://example.com) and text")
        self.assertListEqual([("start", "https://example.com")], matches)

    def test_extract_link_at_end(self):
        matches = extract_markdown_links("text and [end](https://example.com)")
        self.assertListEqual([("end", "https://example.com")], matches)

    def test_extract_links_exclude_images(self):
        text = "This has ![image](https://example.com/img.png) and [link](https://example.com/page)"
        matches = extract_markdown_links(text)
        # Should only extract the link, not the image
        self.assertListEqual([("link", "https://example.com/page")], matches)

    def test_extract_multiple_links_with_images(self):
        text = "![img1](url1) [link1](url1) ![img2](url2) [link2](url2)"
        matches = extract_markdown_links(text)
        expected = [
            ("link1", "url1"),
            ("link2", "url2")
        ]
        self.assertListEqual(expected, matches)

    def test_extract_link_with_complex_url(self):
        matches = extract_markdown_links("[anchor](https://example.com/path?query=value#fragment)")
        self.assertListEqual([("anchor", "https://example.com/path?query=value#fragment")], matches)

    def test_extract_link_with_empty_anchor(self):
        matches = extract_markdown_links("[ ](https://example.com)")
        self.assertListEqual([(" ", "https://example.com")], matches)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_single_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) in the middle",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" in the middle", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_start(self):
        node = TextNode(
            "![start](https://example.com/image.png) and text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("start", TextType.IMAGE, "https://example.com/image.png"),
            TextNode(" and text", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_end(self):
        node = TextNode(
            "text and ![end](https://example.com/image.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("text and ", TextType.TEXT),
            TextNode("end", TextType.IMAGE, "https://example.com/image.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_only_image(self):
        node = TextNode(
            "![only](https://example.com/image.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("only", TextType.IMAGE, "https://example.com/image.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_no_images(self):
        node = TextNode("This is just plain text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("This is just plain text", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_images(self):
        node = TextNode(
            "![img1](url1) text ![img2](url2) more ![img3](url3) end",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("img1", TextType.IMAGE, "url1"),
            TextNode(" text ", TextType.TEXT),
            TextNode("img2", TextType.IMAGE, "url2"),
            TextNode(" more ", TextType.TEXT),
            TextNode("img3", TextType.IMAGE, "url3"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_non_text_node_preserved(self):
        node1 = TextNode("This is text with ![image](url)", TextType.TEXT)
        node2 = TextNode("This is bold", TextType.BOLD)
        node3 = TextNode("More text with ![image2](url2)", TextType.TEXT)
        new_nodes = split_nodes_image([node1, node2, node3])
        expected = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "url"),
            TextNode("This is bold", TextType.BOLD),
            TextNode("More text with ", TextType.TEXT),
            TextNode("image2", TextType.IMAGE, "url2"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_with_empty_alt(self):
        node = TextNode("text ![ ](https://example.com/image.png) more", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("text ", TextType.TEXT),
            TextNode(" ", TextType.IMAGE, "https://example.com/image.png"),
            TextNode(" more", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_with_complex_url(self):
        node = TextNode(
            "text ![alt](https://example.com/path/to/image.png?param=value) more",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("text ", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, "https://example.com/path/to/image.png?param=value"),
            TextNode(" more", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_non_text_nodes(self):
        node1 = TextNode("Bold text", TextType.BOLD)
        node2 = TextNode("Italic text", TextType.ITALIC)
        node3 = TextNode("Code text", TextType.CODE)
        new_nodes = split_nodes_image([node1, node2, node3])
        expected = [node1, node2, node3]
        self.assertListEqual(expected, new_nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_single_link(self):
        node = TextNode(
            "This is text with a [link](https://example.com) in the middle",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" in the middle", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_start(self):
        node = TextNode(
            "[start](https://example.com) and text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("start", TextType.LINK, "https://example.com"),
            TextNode(" and text", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_end(self):
        node = TextNode(
            "text and [end](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("text and ", TextType.TEXT),
            TextNode("end", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_only_link(self):
        node = TextNode(
            "[only](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("only", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_no_links(self):
        node = TextNode("This is just plain text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This is just plain text", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_links(self):
        node = TextNode(
            "[link1](url1) text [link2](url2) more [link3](url3) end",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("link1", TextType.LINK, "url1"),
            TextNode(" text ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "url2"),
            TextNode(" more ", TextType.TEXT),
            TextNode("link3", TextType.LINK, "url3"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_exclude_images(self):
        node = TextNode(
            "This has ![image](https://example.com/img.png) and [link](https://example.com/page)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        # Should only split on the link, not the image
        expected = [
            TextNode("This has ![image](https://example.com/img.png) and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com/page"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_non_text_node_preserved(self):
        node1 = TextNode("This is text with [link](url)", TextType.TEXT)
        node2 = TextNode("This is bold", TextType.BOLD)
        node3 = TextNode("More text with [link2](url2)", TextType.TEXT)
        new_nodes = split_nodes_link([node1, node2, node3])
        expected = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
            TextNode("This is bold", TextType.BOLD),
            TextNode("More text with ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "url2"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_with_empty_anchor(self):
        node = TextNode("text [ ](https://example.com) more", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("text ", TextType.TEXT),
            TextNode(" ", TextType.LINK, "https://example.com"),
            TextNode(" more", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_with_complex_url(self):
        node = TextNode(
            "text [anchor](https://example.com/path?query=value#fragment) more",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("text ", TextType.TEXT),
            TextNode("anchor", TextType.LINK, "https://example.com/path?query=value#fragment"),
            TextNode(" more", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_non_text_nodes(self):
        node1 = TextNode("Bold text", TextType.BOLD)
        node2 = TextNode("Italic text", TextType.ITALIC)
        node3 = TextNode("Code text", TextType.CODE)
        new_nodes = split_nodes_link([node1, node2, node3])
        expected = [node1, node2, node3]
        self.assertListEqual(expected, new_nodes)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_full_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text"
        nodes = text_to_textnodes(text)
        expected = [TextNode("This is just plain text", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_bold_only(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_italic_only(self):
        text = "This is _italic_ text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_code_only(self):
        text = "This is `code` text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_image_only(self):
        text = "This is ![image](https://example.com/img.png) text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_link_only(self):
        text = "This is [link](https://example.com) text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_bold(self):
        text = "**first** and **second** bold"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("first", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("second", TextType.BOLD),
            TextNode(" bold", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_italic(self):
        text = "_first_ and _second_ italic"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("first", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("second", TextType.ITALIC),
            TextNode(" italic", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_nested_delimiters(self):
        text = "This is **bold with _italic_ inside** text"
        nodes = text_to_textnodes(text)
        # Bold is processed first, so italic inside bold won't be processed
        # This is expected behavior - delimiters are processed sequentially
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold with _italic_ inside", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_image_and_link(self):
        text = "![image](https://example.com/img.png) and [link](https://example.com/page)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com/page"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_all_types(self):
        text = "**bold** _italic_ `code` ![img](url) [link](url)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "url"),
            TextNode(" ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_bold_at_start(self):
        text = "**bold** at start"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_bold_at_end(self):
        text = "text at end **bold**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("text at end ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_bold(self):
        text = "**only bold**"
        nodes = text_to_textnodes(text)
        expected = [TextNode("only bold", TextType.BOLD)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_empty_string(self):
        text = ""
        nodes = text_to_textnodes(text)
        expected = [TextNode("", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_images(self):
        text = "![img1](url1) text ![img2](url2)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("img1", TextType.IMAGE, "url1"),
            TextNode(" text ", TextType.TEXT),
            TextNode("img2", TextType.IMAGE, "url2"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_links(self):
        text = "[link1](url1) text [link2](url2)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("link1", TextType.LINK, "url1"),
            TextNode(" text ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "url2"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_complex_combination(self):
        text = "Start **bold** middle _italic_ end `code` ![img](url) [link](url) finish"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" middle ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "url"),
            TextNode(" ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
            TextNode(" finish", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)


if __name__ == "__main__":
    unittest.main()

