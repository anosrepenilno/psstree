from textual.widgets import Tree, Footer, Header
from textual.app import App
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import Mapping, T
    from textual.widget._tree import TreeNode
    from textual.app import ComposeResult

__all__ = ["TreeApp"]



def dfs(parent: "TreeNode", id_: "T", mapping: "Mapping"):
    node = mapping.nodes[id_]
    if len(node.children) == 0:
        textual_node = parent.add_leaf(
            label=node.label,
            data=node,
        )
    else:
        textual_node = parent.add(
            label=node.label,
            data=node,
        )
    for child in node.children:
        dfs(textual_node, child, mapping)


class TreeApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self, 
        mapping: "Mapping",
        expand: bool = False, 
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = "Press q to quit"
        self.mapping = mapping
        self.expand = expand

    def compose(self) -> "ComposeResult":
        yield Header()
        tree: Tree[str] = Tree(label=self.mapping.title)
        for root in self.mapping.roots:
            dfs(tree.root, root, self.mapping)
        tree.root.expand()
        for node in tree.root.children:
            node.expand()
        if self.expand:
            tree.root.expand_all()
        yield tree
        yield Footer()
    