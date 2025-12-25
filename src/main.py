from textnode import TextNode, TextType

def main():
    print("hello world")
    text_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(text_node)

if __name__ == "__main__":
    main()
