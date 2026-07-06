# PSS-tree
```
# python -m psstree --help

usage: __main__.py [-h] [--expand] [--full] [--raw] [--du PATH] [--all]

gets process' PSS via /proc/<PID>/smaps(_rollup), sorts it descendingly within their parent-child hierarchy, and displays it in an interactive TUI with collapsible sections. alternatively can do the same for disk-space usage given a root-path

options:
  -h, --help  show this help message and exit
  --expand    [TUI only] expand all collapsible sections at start
  --full      show full description
  --raw       disable TUI and dump formatted repr directly to stdout
  --du PATH   report disk space instead, for given root-path
  --all       [du only] include content inside certain dirs: site-packages, and ones starting with '.' (like .git) [the dirs themselves are not omitted]

# python -m psstree --raw

Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[16.12MB] bash(7): `2.07MB` 
 │  ├─[13.41MB] python(705): `13.41MB` 
 │  ├─[0.32MB] sleep(703): `0.32MB` 
 │  ╰─[0.32MB] sleep(704): `0.32MB` 
 ╰─[2.14MB] bash(1): `1.51MB` 
    ├─[0.32MB] sleep(700): `0.32MB` 
    ╰─[0.31MB] sleep(702): `0.31MB` 

# python -m psstree --raw --full

Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[16.12MB] bash(7): `2.07MB` bash
 │  ├─[13.41MB] python(706): `13.41MB` python -m psstree --raw --full
 │  ├─[0.32MB] sleep(703): `0.32MB` sleep 100
 │  ╰─[0.32MB] sleep(704): `0.32MB` sleep 100
 ╰─[2.14MB] bash(1): `1.51MB` bash
    ├─[0.32MB] sleep(700): `0.32MB` sleep 100
    ╰─[0.31MB] sleep(702): `0.31MB` sleep 100

# python -m psstree --raw --du .

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.527MB] .
    ├─[0.375MB] .git/*
    ├─[0.113MB] src
    │  ├─[0.094MB] psstree
    │  │  ├─[0.070MB] __pycache__/*
    │  │  ├─[0.008MB] types.py
    │  │  ├─[0.008MB] utils.py
    │  │  ├─[0.004MB] tui.py
    │  │  ╰─[0.004MB] __main__.py
    │  ╰─[0.020MB] psstree.egg-info
    │     ├─[0.004MB] PKG-INFO
    │     ├─[0.004MB] SOURCES.txt
    │     ├─[0.004MB] requires.txt
    │     ├─[0.004MB] top_level.txt
    │     ╰─[0.004MB] dependency_links.txt
    ├─[0.016MB] dist
    │  ├─[0.008MB] psstree-0.1.2.tar.gz
    │  ╰─[0.008MB] psstree-0.1.2-py3-none-any.whl
    ├─[0.004MB] LICENSE
    ├─[0.004MB] Makefile
    ├─[0.004MB] pyproject.toml
    ├─[0.004MB] README.md
    ├─[0.004MB] .gitignore
    ├─[0.004MB] .github/*
    ╰─[0.000MB] images

# python -m psstree --raw --du . --full

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.527MB] .
    ├─[0.375MB] ./.git/*
    ├─[0.113MB] ./src
    │  ├─[0.094MB] ./src/psstree
    │  │  ├─[0.070MB] ./src/psstree/__pycache__/*
    │  │  ├─[0.008MB] ./src/psstree/types.py
    │  │  ├─[0.008MB] ./src/psstree/utils.py
    │  │  ├─[0.004MB] ./src/psstree/tui.py
    │  │  ╰─[0.004MB] ./src/psstree/__main__.py
    │  ╰─[0.020MB] ./src/psstree.egg-info
    │     ├─[0.004MB] ./src/psstree.egg-info/PKG-INFO
    │     ├─[0.004MB] ./src/psstree.egg-info/SOURCES.txt
    │     ├─[0.004MB] ./src/psstree.egg-info/requires.txt
    │     ├─[0.004MB] ./src/psstree.egg-info/top_level.txt
    │     ╰─[0.004MB] ./src/psstree.egg-info/dependency_links.txt
    ├─[0.016MB] ./dist
    │  ├─[0.008MB] ./dist/psstree-0.1.2.tar.gz
    │  ╰─[0.008MB] ./dist/psstree-0.1.2-py3-none-any.whl
    ├─[0.004MB] ./LICENSE
    ├─[0.004MB] ./Makefile
    ├─[0.004MB] ./pyproject.toml
    ├─[0.004MB] ./README.md
    ├─[0.004MB] ./.gitignore
    ├─[0.004MB] ./.github/*
    ╰─[0.000MB] ./images

# python -m psstree --raw --du src/psstree

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.094MB] psstree
    ├─[0.070MB] __pycache__/*
    ├─[0.008MB] types.py
    ├─[0.008MB] utils.py
    ├─[0.004MB] tui.py
    ╰─[0.004MB] __main__.py

# python -m psstree --raw --du src/psstree --all

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.094MB] psstree
    ├─[0.070MB] __pycache__
    │  ├─[0.016MB] utils.cpython-311.pyc
    │  ├─[0.012MB] utils.cpython-314.pyc
    │  ├─[0.012MB] types.cpython-311.pyc
    │  ├─[0.008MB] utils.cpython-39.pyc
    │  ├─[0.008MB] tui.cpython-311.pyc
    │  ├─[0.004MB] __main__.cpython-39.pyc
    │  ├─[0.004MB] tui.cpython-39.pyc
    │  ├─[0.004MB] __main__.cpython-314.pyc
    │  ╰─[0.004MB] __main__.cpython-311.pyc
    ├─[0.008MB] types.py
    ├─[0.008MB] utils.py
    ├─[0.004MB] tui.py
    ╰─[0.004MB] __main__.py
```