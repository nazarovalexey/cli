#!/bin/bash

inclusive=yes
tree=none

path=$(dirname "$0")

if [[ $1 -eq 1 ]];
then
	callgrind_annotate --inclusive=${inclusive} --tree=${tree} ${path}/callgrind.out.1992
elif [[ $1 -eq 2 ]];
then
	callgrind_annotate --inclusive=${inclusive} --tree=${tree} ${path}/callgrind.out.1993
	echo "$0" \[1\|2\]
fi

