from dataclasses import dataclass
from typing import ClassVar, Set, Tuple
import os
import sys
from pathlib import Path

from .utils import BaseNode


@dataclass(kw_only=True)
class PSSNode(BaseNode[int]):
    comm: str
    cmd: str

    title: ClassVar[str] = 'Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"'

    @property
    def label(self):
        suffix = ' '.join(self.cmd) if self.expanded_label else ""
        return f"[{self.total/1024:.2f}MB] {self.comm}({self.id_}): `{self.val/1024:.2f}MB` {suffix}"

    def on_copy(self) -> Tuple[str, str]:
        """
        when user sends ctrl+c on a node,
        (what to copy, what to say has been copied)
        """
        return (
            str(self.id_), 
            "PID"
        )

    @staticmethod
    def is_kernel_thread(pid: int) -> bool:
        PF_KTHREAD = 0x00200000
        try:
            with open(f"/proc/{pid}/stat") as f:
                stat = f.read()

            # Skip "pid (comm)" which may contain spaces/parentheses.
            after_comm = stat[stat.rfind(") ") + 2:]
            fields = after_comm.split()

            # flags is field 9 overall, i.e. index 6 after removing pid+comm
            flags = int(fields[6])

            return bool(flags & PF_KTHREAD)
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            return False
    
    @staticmethod
    def generate_nodes(expanded_label: bool = False):
        import psutil
        for p in psutil.process_iter():
            if PSSNode.is_kernel_thread(p.pid):
                continue
            try:
                info = p.memory_full_info()
            except psutil.AccessDenied:
                continue
            try:
                parent_id = p.ppid()
            except:
                parent_id = 0
            try:
                comm = p.name()
            except:
                comm = "??"
            try:
                cmdline = p.cmdline()
            except:
                cmdline = "??"
            
            yield PSSNode(id_=p.pid, parent_id=parent_id, comm=comm, cmd=cmdline, val=info.pss/1024, expanded_label=expanded_label)


@dataclass(kw_only=True)
class DUNode(BaseNode[str]):
    title: ClassVar[str] = 'Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"'

    UNIMPORTANT_DIRS: ClassVar[Set[str]] = {"site-packages", "__pycache__"}
    
    @staticmethod
    def is_dir_unimportant(name: str) -> bool:
        if name in DUNode.UNIMPORTANT_DIRS:
            return True
        if name.startswith('.') and (set(name) != {'.'}):
            # allow . .. ... but not .git etc
            return True
        return False

    @property
    def label(self):
        if self.expanded_label:
            path = self.id_
        else:
            path = os.path.basename(self.id_)
        if self.collapse_subtree and (len(self.children) > 0):
            path = path+"/*"
        return f"[{self.val/1024:.3f}MB] {path}"

    def on_copy(self) -> Tuple[str, str]:
        """
        when user sends ctrl+c on a node,
        (what to copy, what to say has been copied)
        """
        return (
            str(Path(self.id_).expanduser().resolve()), 
            "absolute path"
        )

    @staticmethod
    def generate_nodes(root_path: str, one_file_system: bool = True, expanded_label: bool = False, include_all: bool = False):
        import subprocess

        cmd = ["du", "-a"]
        if one_file_system:
            cmd.append("-x")
        cmd.append(root_path)

        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            bufsize=1,  # line buffered
        ) as proc:
            assert proc.stdout is not None

            for line in proc.stdout:
                line = line.rstrip("\n")
                if line.strip():
                    size, path = line.strip().split(maxsplit=1)
                    path = path.rstrip("/")
                    parent_path = os.path.dirname(path)
                    assert parent_path != path

                    collapse_subtree = (not include_all) and DUNode.is_dir_unimportant(os.path.basename(path))

                    yield DUNode(
                        id_=path, 
                        parent_id=parent_path, 
                        val=int(size), 
                        total=int(size), 
                        expanded_label=expanded_label, 
                        collapse_subtree=collapse_subtree,
                    )

            rc = proc.wait()
            if rc not in {0, 1}:
                # allowing exit-code 1 since can mean du encountered a non-fatal error but still produced (partial) output
                # for example when some deep subdir denies permission, the rest of the result is still shown without it
                raise subprocess.CalledProcessError(rc, cmd)
