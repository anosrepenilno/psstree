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
```

![PSS Example](https://raw.githubusercontent.com/anosrepenilno/psstree/main/assets/pss.gif)


![DU Example](https://raw.githubusercontent.com/anosrepenilno/psstree/main/assets/du.gif)
