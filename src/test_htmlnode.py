import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):   
    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')
    
    def test_props_to_html_empty(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")
        
        node2 = HTMLNode(props={})
        self.assertEqual(node2.props_to_html(), "")
    
    def test_repr(self):
        node = HTMLNode("p", "Hello", None, {"class": "greeting"})
        expected = "HTMLNode(p, Hello, None, {'class': 'greeting'})"
        self.assertEqual(repr(node), expected)
    
    def test_all_none(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_leaf_node_no_tag(self):
        node = LeafNode(value="Hello")
        self.assertEqual(node.to_html(), "Hello")

    def test_leaf_node_with_tag(self):
        node = LeafNode("p", "Hello", {"class": "greeting"})
        self.assertEqual(node.to_html(), '<p class="greeting">Hello</p>')
    
    def test_leaf_node_to_html(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), '<p>Hello, world!</p>')
    
    def test_leaf_node_raises_value_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertEqual(str(context.exception), "LeafNode must have a value")
    
    def test_parent_node_no_tag(self):
        node = ParentNode(children=[LeafNode("p", "Hello")])
        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertEqual(str(context.exception), "ParentNode must have a tag")
    
    def test_parent_node_no_children(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertEqual(str(context.exception), "ParentNode must have one or more children")
    
    def test_parent_node_single_child(self):
        child = LeafNode("p", "Hello")
        node = ParentNode("div", [child])
        self.assertEqual(node.to_html(), '<div><p>Hello</p></div>')
    
    def test_parent_node_multiple_children(self):
        grand = LeafNode("b", "grandchild")
        child = ParentNode("span", [grand])
        parent = ParentNode("div", [child])
        self.assertEqual(parent.to_html(), '<div><span><b>grandchild</b></span></div>')
    
    def test_parent_node_many_levels(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

if __name__ == "__main__":
    unittest.main()