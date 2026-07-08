# PSS-tree
```
# psstree --help

usage: psstree [-h] [--expand] [--full] [--shm] [--raw] [--du PATH] [--all]

gets process' PSS via /proc/<PID>/smaps(_rollup), sorts it descendingly within their parent-child hierarchy, and displays it in an interactive TUI with collapsible sections. alternatively can do the same for disk-space usage given a root-path

options:
  -h, --help  show this help message and exit
  --expand    [TUI only] expand all collapsible sections at start
  --full      show full description
  --shm       include tmpfs/ramfs filesystems in memory report
  --raw       disable TUI and dump formatted repr directly to stdout
  --du PATH   report disk space instead of memory, for given root-path
  --all       [du only] include content inside certain dirs: site-packages, and ones starting with '.' (like .git) [the dirs themselves are never omitted]

# psstree --raw

Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[16.10MB] bash(291): `2.11MB` 
 │  ├─[13.37MB] psstree(614): `13.37MB` 
 │  ├─[0.31MB] sleep(607): `0.31MB` 
 │  ╰─[0.31MB] sleep(608): `0.31MB` 
 ╰─[2.16MB] bash(1): `1.52MB` 
    ├─[0.32MB] sleep(610): `0.32MB` 
    ╰─[0.32MB] sleep(612): `0.32MB` 

# psstree --raw --shm

Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[16.13MB] bash(291): `2.12MB` 
 │  ├─[13.38MB] psstree(742): `13.38MB` 
 │  ├─[0.32MB] sleep(731): `0.32MB` 
 │  ╰─[0.31MB] sleep(732): `0.31MB` 
 ├─[2.17MB] bash(1): `1.53MB` 
 │  ├─[0.32MB] sleep(728): `0.32MB` 
 │  ╰─[0.32MB] sleep(730): `0.32MB` 
 ├─[0.004MB] /dev/shm/
 │  ╰─[0.004MB] example
 ├─[0.000MB] /dev/
 │  ├─[0.000MB] core
 │  ├─[0.000MB] stderr
 │  ├─[0.000MB] stdout
 │  ├─[0.000MB] stdin
 │  ├─[0.000MB] fd/
 │  ├─[0.000MB] ptmx
 │  ├─[0.000MB] urandom
 │  ├─[0.000MB] zero
 │  ├─[0.000MB] tty
 │  ├─[0.000MB] full
 │  ├─[0.000MB] random
 │  ╰─[0.000MB] null
 ├─[0.000MB] /proc/interrupts
 ├─[0.000MB] /proc/kcore
 ├─[0.000MB] /proc/keys
 ├─[0.000MB] /proc/scsi/
 ├─[0.000MB] /proc/timer_list
 ╰─[0.000MB] /sys/firmware/


# psstree --raw --full

Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[16.10MB] bash(291): `2.11MB` bash
 │  ├─[13.37MB] psstree(633): `13.37MB` /usr/local/bin/python3.11 /usr/local/bin/psstree --raw --full
 │  ├─[0.31MB] sleep(607): `0.31MB` sleep 100
 │  ╰─[0.31MB] sleep(608): `0.31MB` sleep 100
 ╰─[2.16MB] bash(1): `1.52MB` bash
    ├─[0.32MB] sleep(610): `0.32MB` sleep 100
    ╰─[0.32MB] sleep(612): `0.32MB` sleep 100

# psstree --raw --du .

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.629MB] ./
    ├─[0.457MB] .git/*
    ├─[0.129MB] src/
    │  ├─[0.102MB] psstree/
    │  │  ├─[0.074MB] __pycache__/*
    │  │  ├─[0.008MB] types.py
    │  │  ├─[0.008MB] utils.py
    │  │  ├─[0.004MB] cli.py
    │  │  ├─[0.004MB] tui.py
    │  │  ├─[0.004MB] __main__.py
    │  │  ╰─[0.000MB] __init__.py
    │  ╰─[0.027MB] psstree.egg-info/
    │     ├─[0.008MB] PKG-INFO
    │     ├─[0.004MB] SOURCES.txt
    │     ├─[0.004MB] entry_points.txt
    │     ├─[0.004MB] requires.txt
    │     ├─[0.004MB] top_level.txt
    │     ╰─[0.004MB] dependency_links.txt
    ├─[0.016MB] dist/
    │  ├─[0.008MB] psstree-0.1.2.tar.gz
    │  ╰─[0.008MB] psstree-0.1.2-py3-none-any.whl
    ├─[0.008MB] README.md
    ├─[0.004MB] LICENSE
    ├─[0.004MB] Makefile
    ├─[0.004MB] pyproject.toml
    ├─[0.004MB] .gitignore
    ├─[0.004MB] .github/*
    ╰─[0.000MB] images/

# psstree --raw --du . --full

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.629MB] ./
    ├─[0.457MB] ./.git/*
    ├─[0.129MB] ./src/
    │  ├─[0.102MB] ./src/psstree/
    │  │  ├─[0.074MB] ./src/psstree/__pycache__/*
    │  │  ├─[0.008MB] ./src/psstree/types.py
    │  │  ├─[0.008MB] ./src/psstree/utils.py
    │  │  ├─[0.004MB] ./src/psstree/cli.py
    │  │  ├─[0.004MB] ./src/psstree/tui.py
    │  │  ├─[0.004MB] ./src/psstree/__main__.py
    │  │  ╰─[0.000MB] ./src/psstree/__init__.py
    │  ╰─[0.027MB] ./src/psstree.egg-info/
    │     ├─[0.008MB] ./src/psstree.egg-info/PKG-INFO
    │     ├─[0.004MB] ./src/psstree.egg-info/SOURCES.txt
    │     ├─[0.004MB] ./src/psstree.egg-info/entry_points.txt
    │     ├─[0.004MB] ./src/psstree.egg-info/requires.txt
    │     ├─[0.004MB] ./src/psstree.egg-info/top_level.txt
    │     ╰─[0.004MB] ./src/psstree.egg-info/dependency_links.txt
    ├─[0.016MB] ./dist/
    │  ├─[0.008MB] ./dist/psstree-0.1.2.tar.gz
    │  ╰─[0.008MB] ./dist/psstree-0.1.2-py3-none-any.whl
    ├─[0.008MB] ./README.md
    ├─[0.004MB] ./LICENSE
    ├─[0.004MB] ./Makefile
    ├─[0.004MB] ./pyproject.toml
    ├─[0.004MB] ./.gitignore
    ├─[0.004MB] ./.github/*
    ╰─[0.000MB] ./images/

# psstree --raw --du src/psstree

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.102MB] src/psstree/
    ├─[0.074MB] __pycache__/*
    ├─[0.008MB] types.py
    ├─[0.008MB] utils.py
    ├─[0.004MB] cli.py
    ├─[0.004MB] tui.py
    ├─[0.004MB] __main__.py
    ╰─[0.000MB] __init__.py

# psstree --raw --du src/psstree --all

Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.102MB] src/psstree/
    ├─[0.074MB] __pycache__/
    │  ├─[0.016MB] utils.cpython-311.pyc
    │  ├─[0.012MB] utils.cpython-314.pyc
    │  ├─[0.012MB] types.cpython-311.pyc
    │  ├─[0.008MB] utils.cpython-39.pyc
    │  ├─[0.004MB] cli.cpython-311.pyc
    │  ├─[0.004MB] __main__.cpython-39.pyc
    │  ├─[0.004MB] tui.cpython-39.pyc
    │  ├─[0.004MB] __main__.cpython-314.pyc
    │  ├─[0.004MB] tui.cpython-311.pyc
    │  ├─[0.004MB] __init__.cpython-311.pyc
    │  ╰─[0.004MB] __main__.cpython-311.pyc
    ├─[0.008MB] types.py
    ├─[0.008MB] utils.py
    ├─[0.004MB] cli.py
    ├─[0.004MB] tui.py
    ├─[0.004MB] __main__.py
    ╰─[0.000MB] __init__.py
```