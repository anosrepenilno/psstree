from dataclasses import dataclass
from typing import ClassVar, Set, Tuple, List, Any, Dict
import os
import sys
from pathlib import Path

from .utils import BaseNode


@dataclass(kw_only=True)
class PSSNode(BaseNode[int]):
    comm: str
    cmd: List[str]

    mem_info: Any

    title: ClassVar[str] = 'Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"'

    @property
    def label(self):
        suffix = ' '.join(self.cmd) if self.full_description else ""
        return f"[{self.total/1024:.2f}MB] {self.comm}({self.id_}): `{self.val/1024:.2f}MB` {suffix}"

    def on_select(self) -> Tuple[str, str]:
        """
        when user sends ctrl+e on a node, what to display
        """
        return f"PID: {self.id_}, PPID: {self.parent_id}\nPSS (self / total-subtree): {self.val} kB / {self.total} kB\nnum-children: {len(self.children)}\nmem-info (in Bytes): {self.mem_info}\n({self.comm}) {' '.join(self.cmd)}"

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
    def generate_nodes(full_description: bool = False):
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
                cmdline = ["??"]
            
            yield PSSNode(
                id_=p.pid,
                parent_id=parent_id,
                comm=comm,
                cmd=cmdline,
                val=info.pss/1024,
                full_description=full_description,
                mem_info=info,
            )


UNIMPORTANT_DIRS: Set[str] = {"site-packages", "__pycache__"}
ALLOWED_DIRS: Set[str] = {".", "..", "..."}

# ANSI cursor movements:
MOVE_TO_START_OF_LINE = "\r"
CLEAR_LINE = "\033[2K"


@dataclass(kw_only=True)
class DUNode(BaseNode[str]):
    title: ClassVar[str] = 'Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"'

    root_node_overrides: ClassVar[Dict[str, Any]] = {
        "full_description": True,
    }

    is_dir: bool
    
    @staticmethod
    def is_dir_unimportant(name: str) -> bool:
        if name in UNIMPORTANT_DIRS:
            return True
        if name and (name[0] == '.') and (name not in ALLOWED_DIRS):
            # allow . .. ... but not .git etc
            return True
        return False

    @property
    def label(self):
        if self.full_description:
            path = self.id_
        else:
            path = os.path.basename(self.id_)
        
        if self.is_dir and (path != "/"):
            if self.collapse_subtree and (len(self.children) > 0):
                suffix = "/*"
            else:
                suffix = "/"
        else:
            suffix = ""

        return f"[{self.val/1024:.3f}MB] {path}{suffix}"

    def on_select(self) -> Tuple[str, str]:
        """
        when user sends ctrl+e on a node, what to display
        """
        abs_path = str(Path(self.id_).expanduser().resolve())
        if self.is_dir:
            abs_path = abs_path + f"/{{contains {len(self.children)} entries}}"
            
        return f"[{self.val} kB] {abs_path}"

    @staticmethod
    def generate_nodes(root_path: str, one_file_system: bool = True, full_description: bool = False, include_all_dirs: bool = False):
        import subprocess

        cmd = ["du", "-a"]
        if one_file_system:
            cmd.append("-x")
        cmd.append(root_path)

        prefix = f"{MOVE_TO_START_OF_LINE}{CLEAR_LINE}{' '.join(cmd)} :"

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

                print(prefix, line, end="", flush=True)

                if line.strip():
                    size, path = line.strip().split(maxsplit=1)
                    if path != "/":
                        path = path.rstrip("/")
                        parent_path = os.path.dirname(path)
                    else:
                        parent_path = ""
                    assert parent_path != path

                    try:
                        is_dir = os.path.isdir(path)
                    except FileNotFoundError:
                        # maybe it was removed between du output and this check? idk man i'm just some dumbass. why you readin ts
                        is_dir = False

                    collapse_subtree = (not include_all_dirs) and (is_dir) and DUNode.is_dir_unimportant(os.path.basename(path))

                    yield DUNode(
                        id_=path, 
                        parent_id=parent_path, 
                        val=int(size), 
                        total=int(size), 
                        full_description=full_description, 
                        collapse_subtree=collapse_subtree,
                        is_dir=is_dir,
                    )

            rc = proc.wait()
            if rc not in {0, 1}:
                # allowing exit-code 1 since can mean du encountered a non-fatal error but still produced (partial) output
                # for example when some deep subdir denies permission, the rest of the result is still shown without it
                raise subprocess.CalledProcessError(rc, cmd)

        print("")
