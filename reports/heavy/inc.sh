#!/bin/bash

inclusive=yes
tree=none

path=$(dirname "$0")

if [[ $1 -eq 1 ]];
then
	callgrind_annotate --inclusive=${inclusive} --tree=${tree} ${path}/callgrind.out.2003
elif [[ $1 -eq 2 ]];
then
	callgrind_annotate --inclusive=${inclusive} --tree=${tree} ${path}/callgrind.out.2004
elif [[ $1 -eq 3 ]];
then
	callgrind_annotate --inclusive=${inclusive} --tree=${tree} ${path}/callgrind.out.2008
else
	echo "$0" \[1\|2\|3\]
fi

