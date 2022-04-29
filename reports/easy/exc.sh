#!/bin/bash

inclusive=no
tree=none

path=$(dirname "$0")

if [[ $1 -eq 1 ]];
then
	callgrind_annotate --inclusive=${inclusive} --tree=${tree} ${path}/callgrind.out.1992
elif [[ $1 -eq 2 ]];
then
	callgrind_annotate --inclusive=${inclusive} --tree=${tree} ${path}/callgrind.out.1993
else
	echo "$0" \[1\|2\]
fi

