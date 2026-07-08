from textual.widgets import Tree, Footer, Header
from textual.app import App
from textual.binding import Binding

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import Mapping, T
    from textual.widget._tree import TreeNode
    from textual.app import ComposeResult

__all__ = ["TreeApp"]



def dfs(parent: "TreeNode", id_: "T", mapping: "Mapping", expand: bool):
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
            expand=(expand) and (not node.collapse_subtree),
        )
    for child in node.children:
        dfs(textual_node, child, mapping, expand)


class TreeApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        Binding("ctrl+e", "display", "Display", show=True),
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
            dfs(tree.root, root, self.mapping, self.expand)
        tree.root.expand()
        for node in tree.root.children:
            if not node.data.collapse_subtree:
                node.expand()
        yield tree
        yield Footer()

    def action_display(self):
        node = self.query_one(Tree).cursor_node
        if (node is not None) and (node.data is not None):
            text = node.data.on_select()
            with self.suspend():
                import subprocess
                subprocess.run(["less"], input=text.encode())
