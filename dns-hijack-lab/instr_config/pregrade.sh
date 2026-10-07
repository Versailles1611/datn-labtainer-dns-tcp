#!/bin/bash
: <<'END'
This software was written for the NPS Labtainers project.
License: public domain.
END
homedir=$1
destdir=$2
dbg=/tmp/pregrade.log
cd $homedir/$destdir
# No preprocessing required for this lab.
exit 0
