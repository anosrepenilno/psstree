import argparse
from dataclasses import dataclass
from typing import Optional

from .utils import Mapping
from .types import PSSNode, DUNode


@dataclass
class PSSArgs:
    include_shm: bool


@dataclass
class DUArgs:
    root_path: str
    include_all_dirs: bool


@dataclass
class Args:
    # common args:
    full_description: bool
    display_tui: bool

    pss_args: Optional[PSSArgs] = None
    du_args: Optional[DUArgs] = None


def parse_args():
    parser = argparse.ArgumentParser(description="""
    gets process' PSS via /proc/<PID>/smaps(_rollup), sorts it descendingly within their parent-child hierarchy, 
    and displays it in an interactive TUI with collapsible sections.
    alternatively can do the same for disk-space usage given a root-path
    """)

    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="show full description in labels"
    )

    parser.add_argument(
        "--shm",
        action="store_true",
        default=False,
        help="include tmpfs/ramfs filesystems in memory report"
    )

    parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="disable TUI and dump formatted repr directly to stdout"
    )

    parser.add_argument(
        "--du",
        metavar="PATH",
        help="report disk space instead of memory, for given root-path",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="[only matters for --raw --du] include content inside certain noisy/unimportant dirs: currently this includes site-packages, __pycache__, and ones starting with '.' (like .git). by default it is omitted (the dirs themselves are never omitted, just that they would be collapsed)"
    )

    cmdline_args = parser.parse_args()

    args = Args(
        full_description=cmdline_args.full,
        display_tui=(not cmdline_args.raw),
    )
    if cmdline_args.du is None:
        if args.display_tui:
            args.full_description = True
        args.pss_args = PSSArgs(
            include_shm=cmdline_args.shm
        )
    else:
        args.du_args = DUArgs(
            root_path=cmdline_args.du,
            include_all_dirs=cmdline_args.all
        )
        if args.display_tui:
            args.du_args.include_all_dirs = True

    return args


def main():
    args: Args = parse_args()

    mapping  = Mapping()

    if args.pss_args is not None:
        mapping.add_nodes(
            node_cls=PSSNode, 
            node_kwargs={
                "full_description": args.full_description,
            },
            skip_sort_roots=args.pss_args.include_shm,
        )
        if args.pss_args.include_shm:
            import psutil

            mounts = sorted(
                partition.mountpoint
                for partition in psutil.disk_partitions(all=True)
                if partition.fstype in {"tmpfs", "ramfs"}
            )

            for mount in mounts:
                if mount in mapping.nodes:
                    # if a child path is a separate mount entry than
                    # a parent path but the parent path's `du -x` result
                    # included the child path anyway, we just assume the 
                    # parent path `du -x` is correct
                    continue
                mapping.add_nodes(
                    node_cls=DUNode, 
                        node_kwargs={
                        "root_path": mount,
                        "include_all_dirs": True,
                    },
                    skip_sort_roots=True,
                )

            mapping.sort_roots()

    elif args.du_args is not None:
        mapping.add_nodes(
            node_cls=DUNode, 
            node_kwargs={
                "root_path": args.du_args.root_path, 
                "full_description": args.full_description, 
                "include_all_dirs": args.du_args.include_all_dirs,
            },
            skip_sort_roots=False,
        ) 
    else:
        return

    mapping.update_total()

    if args.display_tui:
        from .tui import TreeApp
        app = TreeApp(mapping=mapping)
        app.run()
    else:
        print(mapping.get_repr(), flush=True)

    