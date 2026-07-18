# PSS-tree
```
root@8c5c99474e16:/opt/dev# psstree --help
usage: psstree [-h] [--full] [--shm] [--raw] [--du PATH] [--all]

gets process' PSS via /proc/<PID>/smaps(_rollup), sorts it descendingly within their parent-child hierarchy, and displays it in an interactive TUI with collapsible sections. alternatively can do the same for disk-space usage given a root-path

options:
  -h, --help  show this help message and exit
  --full      show full description in labels
  --shm       include tmpfs/ramfs filesystems in memory report
  --raw       disable TUI and dump formatted repr directly to stdout
  --du PATH   report disk space instead of memory, for given root-path
  --all       [only matters for --raw --du] include content inside certain noisy/unimportant dirs: currently this includes site-packages, __pycache__, and ones starting with '.' (like .git). by default it is omitted (the dirs themselves are
              never omitted, just that they would be collapsed)
root@8c5c99474e16:/opt/dev# psstree --raw 
[total 18.51MB] Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[16.34MB] bash(118): `2.14MB` 
 │  ├─[13.56MB] psstree(708): `13.56MB` 
 │  ├─[0.32MB] sleep(707): `0.32MB` 
 │  ╰─[0.31MB] sleep(706): `0.31MB` 
 ╰─[2.17MB] bash(1): `1.54MB` 
    ├─[0.32MB] sleep(705): `0.32MB` 
    ╰─[0.32MB] sleep(703): `0.32MB` 
root@8c5c99474e16:/opt/dev# psstree --raw --full
[total 18.51MB] Proportional Set Size (PSS) "[<total-PSS-including-all-children>] command-name(pid): `<individual-PSS>` <full-cmdline-args>"
 ╭─[16.34MB] bash(118): `2.14MB` bash
 │  ├─[13.57MB] psstree(709): `13.57MB` /usr/local/bin/python3.11 /usr/local/bin/psstree --raw --full
 │  ├─[0.32MB] sleep(707): `0.32MB` sleep 100
 │  ╰─[0.31MB] sleep(706): `0.31MB` sleep 100
 ╰─[2.17MB] bash(1): `1.54MB` bash
    ├─[0.32MB] sleep(705): `0.32MB` sleep 100
    ╰─[0.32MB] sleep(703): `0.32MB` sleep 100
root@8c5c99474e16:/opt/dev# psstree --raw --du psstree/src/
du -a -x psstree/src/ : 144	psstree/src/
[total 0.14MB] Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.141MB] psstree/src/
    ├─[0.113MB] psstree/
    │  ├─[0.082MB] __pycache__/*
    │  ├─[0.008MB] types.py
    │  ├─[0.008MB] cli.py
    │  ├─[0.008MB] utils.py
    │  ├─[0.004MB] tui.py
    │  ├─[0.004MB] __main__.py
    │  ╰─[0.000MB] __init__.py
    ╰─[0.027MB] psstree.egg-info/
       ├─[0.008MB] PKG-INFO
       ├─[0.004MB] SOURCES.txt
       ├─[0.004MB] entry_points.txt
       ├─[0.004MB] requires.txt
       ├─[0.004MB] top_level.txt
       ╰─[0.004MB] dependency_links.txt
root@8c5c99474e16:/opt/dev# psstree --raw --du psstree/src/ --full
du -a -x psstree/src/ : 144	psstree/src/
[total 0.14MB] Disk-Space usage "[<total-space-including-subdirs-recursively>] <path>"
 ╶─[0.141MB] psstree/src/
    ├─[0.113MB] psstree/src/psstree/
    │  ├─[0.082MB] psstree/src/psstree/__pycache__/*
    │  ├─[0.008MB] psstree/src/psstree/types.py
    │  ├─[0.008MB] psstree/src/psstree/cli.py
    │  ├─[0.008MB] psstree/src/psstree/utils.py
    │  ├─[0.004MB] psstree/src/psstree/tui.py
    │  ├─[0.004MB] psstree/src/psstree/__main__.py
    │  ╰─[0.000MB] psstree/src/psstree/__init__.py
    ╰─[0.027MB] psstree/src/psstree.egg-info/
       ├─[0.008MB] psstree/src/psstree.egg-info/PKG-INFO
       ├─[0.004MB] psstree/src/psstree.egg-info/SOURCES.txt
       ├─[0.004MB] psstree/src/psstree.egg-info/entry_points.txt
       ├─[0.004MB] psstree/src/psstree.egg-info/requires.txt
       ├─[0.004MB] psstree/src/psstree.egg-info/top_level.txt
       ╰─[0.004MB] psstree/src/psstree.egg-info/dependency_links.txt
```