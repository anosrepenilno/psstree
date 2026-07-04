from textual.widgets import Tree, Footer, Header
from textual.app import App
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import Mapping
    from textual.widget._tree import TreeNode
    from textual.app import ComposeResult

__all__ = ["TreeApp"]



def dfs(parent: "TreeNode", pid: int, mapping: "Mapping"):
    proc = mapping.PROCS[pid]
    node = parent.add(
        label=proc.label,
        data=proc,
    )
    for child in proc.children:
        dfs(node, child, mapping)


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
        tree: Tree[str] = Tree(label="PSS (Proportional Set Size) `command(pid): <individual-PSS>/<total-PSS-including-all-children>`")
        for root in self.mapping.ROOTS:
            dfs(tree.root, root, self.mapping)
        tree.root.expand()
        for node in tree.root.children:
            node.expand()
        if self.expand:
            tree.root.expand_all()
        yield tree
        yield Footer()
    