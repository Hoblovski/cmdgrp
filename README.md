# CmdGrp
Easily create command groups like `git init`.

# Usage
Install python3, and

```
$ ./cmdgrp.py -i example.cmdgrp -o example.sh
$ ex
$ ex hello
$ ex greet
$ ex greet normal tom
$ ex util seq 12
```

# CmdGrp file format
See `example.cmdgrp` for help.

* Whole-line comments start with `----`
  - Usually this should not clash with commands but just in case this can be
    configured with `-c` option
* Empty lines are ignored.
* Indentation must use tabs i.e. `\t`
* Commands should be bash commands.
* To define a command fragment, write `<name>:` 
* To define a subcommand fragment, do the same except with one more level of indentation
* To define a terminal command, write `<name>.` followed by several lines of actual script, 
  each has exactly one more level of indentation than `<name>.`
