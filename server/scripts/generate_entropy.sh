#!/bin/bash

size=$1
if [[ -z "$size" ]]; then
	echo "Use: "$0" size_in_bytes"
	exit 1
fi 

cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w "$size" | head -n "$size"
exit 0
