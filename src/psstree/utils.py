import os
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Generic, TypeVar, ClassVar, Type, Tuple


T = TypeVar("T")

@dataclass(kw_only=True)
class BaseNode(Generic[T]):
    id_: T
    parent_id: T
    val: int

    depth: int = 0 # distance from root node
    children: List[T] = field(default_factory=list) # `id_` of children
    traversal_order: List[T] = field(default_factory=list) # dfs traversal order sorted w.r.t `total`
    total: Optional[int] = None # if None, filled as sum of `val` of this subtree

    title: ClassVar[str] = ""
    
    expanded_label: bool = False
    collapse_subtree: bool = False
    
    @property
    def label(self):
        raise NotImplementedError

    @staticmethod
    def generate_nodes():
        raise NotImplementedError

    def on_select(self) -> str:
        """
        when user sends ctrl+e on a node, what to display
        """
        return self.label


def get_indents(depths):
    @dataclass
    class Cell:
        left: bool = False
        right: bool = False
        top: bool = False
        bottom: bool = False
        
        def char(self) -> str:
            return {
                (False, False, False, False): "   ",
                (False, False, False, True): " ╷ ",
                (False, False, True, False): " ╵ ",
                (False, False, True, True): " │ ",
                (False, True, False, False): " ╶─",
                (False, True, False, True): " ╭─",
                (False, True, True, False): " ╰─",
                (False, True, True, True): " ├─",
                (True, False, False, False): "─╴ ",
                (True, False, False, True): "─╮ ",
                (True, False, True, False): "─╯ ",
                (True, False, True, True): "─┤ ",
                (True, True, False, False): "───",
                (True, True, False, True): "─┬─",
                (True, True, True, False): "─┴─",
                (True, True, True, True): "─┼─",
            }[(
                self.left,
                self.right,
                self.top,
                self.bottom,
            )]

    indents = [[Cell() for _ in range(depth+1)] for depth in depths]    
    size = len(depths)

    assert min(depths) == 0

    last_occurence = [None]*(max(depths) + 1)

    for idx, depth in enumerate(depths):
        if (
            (last_occurence[depth] is not None) 
            and 
            (
                (depth==0) 
                or 
                (last_occurence[depth] > last_occurence[depth-1])
            )
        ):
            last = last_occurence[depth]
            for i in range(last, idx):
                indents[i][depth].bottom = True
            for i in range(last+1, idx+1):
                indents[i][depth].top = True
        last_occurence[depth] = idx

    for idx, depth in enumerate(depths):
        indents[idx][depth].right = True

    for idx in range(size-1):
        if depths[idx] < depths[idx+1]:
            assert depths[idx+1] == 1 + depths[idx]
            depth = depths[idx]
            indents[idx+1][depth+1].top = True

    return [
        "".join([cell.char() for cell in indent])
        for indent in indents
    ]


class Mapping:
    def __init__(self, node_cls: Type[BaseNode[T]], node_kwargs: Dict[str, str] = {}):
        self.nodes: Dict[T, BaseNode[T]] = {}
        self.roots: List[T] = []
        self.traversal_order: Optional[List[T]] = None
        self.title: str = "<??>"
        self.repr: str = "<??>"

        self.node_cls: Type[BaseNode[T]] = node_cls
        self.node_kwargs: Dict[str, str] = node_kwargs

    def dfs(self, id_: T, depth: int, visited: Set[T], visiting: Set[T]):
        if id_ in visiting:
            raise ValueError(f"circular reference \n{id_=}, {depth=}, {visited=}, {visiting=}, {self.roots=}, {self.nodes=}\n circular reference")
        
        if id_ in visited:
            raise ValueError(f"multiple parents \n{id_=}, {depth=}, {visited=}, {visiting=}, {self.roots=}, {self.nodes=}\n multiple parents")

        visiting.add(id_)

        node = self.nodes[id_]
        
        for child in node.children:
            self.dfs(child, depth+1, visited, visiting)
            
        node.depth = depth
        node.children.sort(key=lambda id: self.nodes[id].total, reverse=True)
        node.traversal_order = sum((self.nodes[child].traversal_order for child in node.children), start=[id_])
        if node.total is None:
            node.total = sum((self.nodes[child].total for child in node.children), start=node.val)

        visiting.remove(id_)
        visited.add(id_)

    def is_in_collapsed_subtree(self, id_: T):
        """
        only if `id_` is part of the *inside* of the collapsed subtree. 
        the root of that subtree will return False. (unless ofcourde it too has a parent which collapses it)
        """
        node = self.nodes[id_]
        id_ = node.parent_id
        
        while id_ in self.nodes:
            node = self.nodes[id_]
            if node.collapse_subtree:
                return True
            id_ = node.parent_id
        
        return False
    
    def create(self, repr=False, expand_root_labels=False):
        self.nodes.clear()
        self.roots.clear()

        for node in self.node_cls.generate_nodes(**self.node_kwargs):
            self.nodes[node.id_] = node

        for node in self.nodes.values():
            if node.parent_id in self.nodes:
                self.nodes[node.parent_id].children.append(node.id_)
            else:
                self.roots.append(node.id_)
        
        for root in self.roots:
            self.dfs(root, 0, set(), set())

        self.roots.sort(key=lambda pid: self.nodes[pid].total, reverse=True)
        self.traversal_order = sum((self.nodes[root].traversal_order for root in self.roots), start=[])

        self.title = self.node_cls.title

        if expand_root_labels:
            for root in self.roots:
                self.nodes[root].expanded_label = True

        if not repr:
            return

        self.traversal_order = [
            id_ 
            for id_ in self.traversal_order
            if not self.is_in_collapsed_subtree(id_)
        ]
        
        indents = get_indents([self.nodes[id_].depth for id_ in self.traversal_order])
        
        self.repr = "\n".join([self.title] + [
            indent + self.nodes[id_].label 
            for indent, id_ in zip(indents, self.traversal_order)
        ])

