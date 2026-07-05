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
        help="[TUI only] expand all collapsible sections at start"
    )

    parser.add_argument(
        "--raw",
        action="store_true",
        help="disable TUI and dump formatted repr directly to stdout"
    )

    parser.add_argument(
        "--du",
        metavar="PATH",
        help="report disk space instead, for given root-path",
    )

    args = parser.parse_args()

    if args.du is None:
        mapping = Mapping(node_cls=PSSNode)
    else:
        mapping = Mapping(node_cls=DUNode, node_kwargs={"root_path": args.du})
    
    mapping.create(repr=True)
    raw_output = mapping.repr

    if args.raw:
        print(raw_output, flush=True)
    else:
        try:
            from .tui import TreeApp
            app = TreeApp(mapping=mapping, expand=args.expand)
            app.run()
        except Exception:
            print(raw_output, flush=True)
            raise

    