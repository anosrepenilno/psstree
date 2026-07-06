import argparse

from .utils import Mapping
from .types import PSSNode, DUNode

if __name__ == "__main__":
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
        "--raw",
        action="store_true",
        default=False,
        help="disable TUI and dump formatted repr directly to stdout"
    )

    parser.add_argument(
        "--du",
        metavar="PATH",
        help="report disk space instead, for given root-path",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="[du only] include content inside certain dirs: site-packages, and ones starting with '.' (like .git) [the dirs themselves are not omitted]"
    )

    args = parser.parse_args()

    if args.du is None:
        if not args.raw:
            args.full = True
        mapping = Mapping(node_cls=PSSNode, node_kwargs={"expanded_label": args.full})
    else:
        mapping = Mapping(node_cls=DUNode, node_kwargs={
            "root_path": args.du, 
            "expanded_label": args.full, 
            "include_all": args.all,
        })
    
    mapping.create(repr=args.raw)

    if args.raw:
        print(mapping.repr, flush=True)
    else:
        from .tui import TreeApp
        app = TreeApp(mapping=mapping, expand=args.expand)
        app.run()

    