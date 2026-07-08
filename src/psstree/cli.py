import argparse

from .utils import Mapping
from .types import PSSNode, DUNode

def main():
    parser = argparse.ArgumentParser(description="""
    gets process' PSS via /proc/<PID>/smaps(_rollup), sorts it descendingly within their parent-child hierarchy, 
    and displays it in an interactive TUI with collapsible sections.
    alternatively can do the same for disk-space usage given a root-path
    """)

    parser.add_argument(
        "--expand",
        action="store_true",
        default=False,
        help="[TUI only] expand all collapsible sections at start"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="show full description"
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
        help="[du only] include content inside certain dirs: site-packages, and ones starting with '.' (like .git) [the dirs themselves are never omitted]"
    )

    args = parser.parse_args()

    if args.du is None:
        if not args.raw:
            args.full = True
        mapping = Mapping(node_cls=PSSNode, node_kwargs={
            "expanded_label": args.full,
        })
    else:
        mapping = Mapping(node_cls=DUNode, node_kwargs={
            "root_path": args.du, 
            "expanded_label": args.full, 
            "include_all": args.all,
        }) 
    
    mapping.clear()
    mapping.create()

    if args.shm:
        import psutil
        for partition in psutil.disk_partitions(all=True):
            if partition.fstype in {"tmpfs", "ramfs"}:
                mapping_shm = Mapping(node_cls=DUNode, node_kwargs={
                    "root_path": partition.mountpoint,
                    "include_all": True,
                })
                mapping_shm.clear()
                mapping_shm.create()
                for id_, node in mapping_shm.nodes.items():
                    if id_ in mapping.nodes:
                        raise ValueError(
                            f"generated duplicate id={id_} by {node=} when there is existing node={mapping.nodes[id_]}"
                        )
                    mapping.nodes[id_] = node
                for root in mapping_shm.roots:
                    mapping.roots.append(root)
                    mapping.nodes[root].expanded_label = True
        mapping.sort_roots()

    if args.du is not None:
        for root in mapping.roots:
            mapping.nodes[root].expanded_label = True

    if args.raw:
        print(mapping.get_repr(), flush=True)
    else:
        from .tui import TreeApp
        app = TreeApp(mapping=mapping, expand=args.expand)
        app.run()

    