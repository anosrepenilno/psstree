from dataclasses import dataclass
from typing import ClassVar
import os

from .utils import BaseNode


@dataclass(kw_only=True)
class PSSNode(BaseNode[int]):
    comm: str
    cmd: str

    title: ClassVar[str] = 'Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"'

    @property
    def label(self):
        return f"[{self.total/1024:.2f}MB] {self.comm}({self.id_}): `{self.val/1024:.2f}MB` {self.cmd}"

    @staticmethod
    def generate_nodes():
        import psutil
        for p in psutil.process_iter():
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
            
            yield PSSNode(id_=p.pid, parent_id=parent_id, comm=comm, cmd=cmdline, val=info.pss/1024)


@dataclass(kw_only=True)
class DUNode(BaseNode[str]):
    title: ClassVar[str] = 'Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"'

    @property
    def label(self):
        return f"[{self.val/1024:.3f}MB] {self.id_}"

    @staticmethod
    def generate_nodes(root_path: str, one_file_system: bool = True):
        import subprocess

        cmd = ["du", "-a"]
        if one_file_system:
            cmd.append("-x")
        cmd.append(root_path)

        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
                    yield DUNode(id_=path, parent_id=parent_path, val=int(size), total=int(size))

            rc = proc.wait()
            if rc != 0:
                stderr = proc.stderr.read() if proc.stderr else ""
                raise subprocess.CalledProcessError(rc, cmd, stderr=stderr)
