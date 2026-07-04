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
    size = len(depths)

    # depths[ < 0 ] -> infty
    # depths[ >= size ] -> -1

    result = []

    for idx in range(size):
        if idx>0 and depths[idx-1] < depths[idx]:
            start = "  "*(depths[idx]-1) + "╰─"
            if (idx+1)<size and depths[idx] <= depths[idx+1]:
                start += "┬─"
            else:
                start += "──"
        elif idx>0 and depths[idx-1] == depths[idx]:
            start = "  "*depths[idx] 
            if (idx+1)<size and depths[idx] <= depths[idx+1]:
                start += "├─"
            else:
                start += "╰─"
        elif idx==0 or depths[idx-1] > depths[idx]:
            start = "  "*depths[idx] 
            if (idx+1)<size and depths[idx] <= depths[idx+1]:
                start += "┌─"
            else:
                start += "──"
        
        result.append(start)
    
    return result
        

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
            line.strip().split() 
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

