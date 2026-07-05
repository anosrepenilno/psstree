import os
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional

@dataclass
class Proc:
    pid: int
    ppid: int
    comm: str
    val: int

    depth: int = 0
    children: List[int] = field(default_factory=list)
    traversal_order: List[str] = field(default_factory=list)
    total: int = 0
    label: str = "<??>"


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
    def __init__(self):
        self.PROCS: Dict[int, Proc] = {}
        self.ROOTS: List[int] = []
        self.traversal_order: Optional[List[int]] = None
        self.repr: str = "<??>"

    def dfs(self, pid: int, depth: int, visited: Set[int], visiting: Set[int]):
        if pid in visiting:
            raise ValueError(f"circular reference \n{pid=}, {depth=}, {visited=}, {visiting=}, {self.ROOTS=}, {self.PROCS=}\n circular reference")
        
        if pid in visited:
            raise ValueError(f"multiple parents \n{pid=}, {depth=}, {visited=}, {visiting=}, {self.ROOTS=}, {self.PROCS=}\n multiple parents")

        visiting.add(pid)

        proc = self.PROCS[pid]
        
        for child in proc.children:
            self.dfs(child, depth+1, visited, visiting)
            
        proc.depth = depth
        proc.children.sort(key=lambda id: self.PROCS[id].total, reverse=True)
        proc.traversal_order = sum((self.PROCS[child].traversal_order for child in proc.children), start=[pid])
        proc.total = sum((self.PROCS[child].total for child in proc.children), start=proc.val)
        proc.label = f"{proc.comm}({proc.pid}): {proc.val/1024:.2f}MB/{proc.total/1024:.2f}MB"

        visiting.remove(pid)
        visited.add(pid)


    def create(self, repr=False):
        self.PROCS.clear()
        self.ROOTS.clear()

        lines = [
            line.strip().split() 
            for line in subprocess.check_output(
                ["smem", "-c", "pid pss", "-H"], 
                text=True
            ).splitlines()
            if line.strip()
        ]
        
        PSSs = {int(line[0]): int(line[1]) for line in lines}

        lines = [
            line.strip().split(maxsplit=2) 
            for line in subprocess.check_output(
                ["ps", "-eo", "pid,ppid,comm", "--no-header"], 
                text=True
            ).splitlines() 
            if line.strip()
        ]

        for pid, ppid, comm in lines:
            pid = int(pid)
            ppid = int(ppid)
            if pid not in PSSs:
                continue
            self.PROCS[pid] = Proc(pid=pid, ppid=ppid, comm=comm, val=PSSs[pid])

        for proc in self.PROCS.values():
            if proc.ppid in self.PROCS:
                self.PROCS[proc.ppid].children.append(proc.pid)
            else:
                self.ROOTS.append(proc.pid)
        
        for root in self.ROOTS:
            self.dfs(root, 0, set(), set())

        self.ROOTS.sort(key=lambda pid: self.PROCS[pid].total, reverse=True)
        self.traversal_order = sum((self.PROCS[root].traversal_order for root in self.ROOTS), start=[])

        if repr:
            indents = get_indents([self.PROCS[pid].depth for pid in self.traversal_order])
            
            self.repr = "\n".join([
                indent + self.PROCS[pid].label 
                for indent, pid in zip(indents, self.traversal_order)
            ])

