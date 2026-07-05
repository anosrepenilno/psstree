# PSS-tree
```
# python -m psstree --help

usage: __main__.py [-h] [--expand] [--raw] [--du PATH]

gets process' PSS via /proc/<PID>/smaps(_rollup), sorts it descendingly within their parent-child hierarchy, and displays it in an interactive TUI with collapsible sections. alternatively can do the same for disk-space usage given a root-path


options:
  -h, --help  show this help message and exit
  --expand    [TUI only] expand all collapsible sections at start
  --raw       disable TUI and dump formatted repr directly to stdout
  --du PATH   report disk space instead, for given root-path

# python -m psstree --raw

Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[15.78MB] bash(7): `2.06MB` ['bash']
 │  ├─[12.77MB] python(148): `12.77MB` ['python', '-m', 'psstree', '--raw']
 │  ├─[0.32MB] sleep(144): `0.32MB` ['sleep', '10']
 │  ├─[0.31MB] sleep(143): `0.31MB` ['sleep', '10']
 │  ╰─[0.31MB] sleep(145): `0.31MB` ['sleep', '10']
 ╰─[1.83MB] bash(1): `1.51MB` ['bash']
    ╰─[0.32MB] sleep(147): `0.32MB` ['sleep', '10']

# python -m psstree --raw --du ./src/

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.098MB] ./src
    ├─[0.078MB] ./src/psstree
    │  ├─[0.059MB] ./src/psstree/__pycache__
    │  │  ├─[0.012MB] ./src/psstree/__pycache__/utils.cpython-314.pyc
    │  │  ├─[0.012MB] ./src/psstree/__pycache__/utils.cpython-311.pyc
    │  │  ├─[0.008MB] ./src/psstree/__pycache__/utils.cpython-39.pyc
    │  │  ├─[0.008MB] ./src/psstree/__pycache__/types.cpython-311.pyc
    │  │  ├─[0.004MB] ./src/psstree/__pycache__/__main__.cpython-39.pyc
    │  │  ├─[0.004MB] ./src/psstree/__pycache__/tui.cpython-39.pyc
    │  │  ├─[0.004MB] ./src/psstree/__pycache__/__main__.cpython-314.pyc
    │  │  ├─[0.004MB] ./src/psstree/__pycache__/tui.cpython-311.pyc
    │  │  ╰─[0.004MB] ./src/psstree/__pycache__/__main__.cpython-311.pyc
    │  ├─[0.008MB] ./src/psstree/utils.py
    │  ├─[0.004MB] ./src/psstree/types.py
    │  ├─[0.004MB] ./src/psstree/tui.py
    │  ╰─[0.004MB] ./src/psstree/__main__.py
    ╰─[0.020MB] ./src/psstree.egg-info
       ├─[0.004MB] ./src/psstree.egg-info/PKG-INFO
       ├─[0.004MB] ./src/psstree.egg-info/SOURCES.txt
       ├─[0.004MB] ./src/psstree.egg-info/requires.txt
       ├─[0.004MB] ./src/psstree.egg-info/top_level.txt
       ╰─[0.004MB] ./src/psstree.egg-info/dependency_links.txt
```