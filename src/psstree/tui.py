from textual.widgets import Tree, Footer, Header
from rich.text import Text
from textual.app import App
from textual.binding import Binding

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import Mapping, T
    from textual.widget._tree import TreeNode
    from textual.app import ComposeResult

__all__ = ["TreeApp"]



def add_child(parent: "TreeNode", id_: "T", mapping: "Mapping") -> "TreeNode":
    node = mapping.nodes[id_]
    if len(node.children) == 0:
        textual_node = parent.add_leaf(
            label=node.label,
            data={"children_populated": True, "underlying_node": node},
        )
    else:
        textual_node = parent.add(
            label=node.label,
            data={"children_populated": False, "underlying_node": node},
            expand=False,
        )
        # recursive addition of children is done lazily. just like after urbanisation in developed country's cities. sorry.
    return textual_node


class TreeApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        Binding("ctrl+e", "display", "Display", show=True),
    ]

    def __init__(
        self, 
        mapping: "Mapping",
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = "Press q to quit"
        self.mapping = mapping

    def compose(self) -> "ComposeResult":
        yield Header()
        # rich.text.Text because textual tries to render stuff inside square brackets: []
        tree: Tree[str] = Tree(label=Text(self.mapping.title))
        for root in self.mapping.roots:
            add_child(tree.root, root, self.mapping)
        tree.root.expand()
        if len(tree.root.children) == 1:
            # cosmetic
            tree.root.children[0].expand()
        yield tree
        yield Footer()

    def action_display(self):
        node = self.query_one(Tree).cursor_node
        if (node is not None) and (node.data is not None):
            text = node.data.on_select()
            with self.suspend():
                import subprocess
                subprocess.run(["less"], input=text.encode())

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        node = event.node

        if node.data is None:
            return

        if node.data["children_populated"]:
            return

        node.data["children_populated"] = True

        for child in node.data["underlying_node"].children:
            add_child(node, child, self.mapping)
