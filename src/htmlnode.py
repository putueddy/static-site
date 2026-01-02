class HTMLNode:
    def __init__(self, tag: str = None, value: str = None, children: list["HTMLNode"] = None, props: dict[str, str] = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def to_html(self):
        raise NotImplementedError("to_html method not implemented")
    
    def props_to_html(self) -> str:
        if self.props is None or not self.props:
            return ""
        return " " + " ".join([f'{key}="{value}"' for key, value in self.props.items()])

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag: str = None, value: str = None, props: dict[str, str] = None):
        super().__init__(tag, value, None, props)
    
    def to_html(self):
        if self.tag is None:
            if self.value is None:
                raise ValueError("LeafNode must have a value or a tag")
            return self.value
        # Handle self-closing tags (like img)
        if self.tag == "img":
            if self.value is None or self.value == "":
                return f"<{self.tag}{self.props_to_html()}>"
            return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag: str = None, children: list["HTMLNode"] = None, props: dict[str, str] = None):
        super().__init__(tag, None, children, props)
    
    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        if self.children is None or len(self.children) == 0:
            raise ValueError("ParentNode must have one or more children")
        
        children_html = "".join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"