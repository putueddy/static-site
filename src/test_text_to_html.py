import unittest
from textnode import TextNode, TextType, text_node_to_html_node

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        text_node = TextNode("Hello world", TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "Hello world")
        self.assertEqual(html_node.props, None)
    
    def test_bold(self):
        text_node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")
        self.assertEqual(html_node.props, None)
    
    def test_italic(self):
        text_node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")
        self.assertEqual(html_node.props, None)
    
    def test_code(self):
        text_node = TextNode("print('hello')", TextType.CODE)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('hello')")
        self.assertEqual(html_node.props, None)
    
    def test_link(self):
        text_node = TextNode("Click me", TextType.LINK, "https://www.example.com")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click me")
        self.assertEqual(html_node.props, {"href": "https://www.example.com"})
    
    def test_link_no_url(self):
        text_node = TextNode("Click me", TextType.LINK)
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(text_node)
        self.assertEqual(str(context.exception), "Link TextNode must have a URL")
    
    def test_image(self):
        text_node = TextNode("Alt text", TextType.IMAGE, "https://www.example.com/image.png")
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, None)
        self.assertEqual(html_node.props, {"src": "https://www.example.com/image.png", "alt": "Alt text"})
    
    def test_image_no_url(self):
        text_node = TextNode("Alt text", TextType.IMAGE)
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(text_node)
        self.assertEqual(str(context.exception), "Image TextNode must have a URL")
    
    def test_unsupported_type(self):
        # Create a mock unsupported text type
        text_node = TextNode("test", "unsupported_type")
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(text_node)
        self.assertIn("Unsupported text type", str(context.exception))

if __name__ == "__main__":
    unittest.main()
