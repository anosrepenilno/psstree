import argparse

from .utils import Mapping

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gets process' PSS via smem, sorts it descendingly within their parent-child hierarchy, and displays it in an interactive TUI with collapsible sections")

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

    args = parser.parse_args()

    mapping = Mapping()
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

    