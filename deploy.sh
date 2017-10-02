#!/usr/bin/env bash

# get all of the variables out of the env
# and split them on "=" to get the first half
# then join them with a space
variables=$(env \
	| awk '{split($1,e,"="); print "$"e[1]}' \
	| tr '\n' ' ')

envsubst "$variables" < "config.template" > "config.yaml"

lambda deploy --use-requirements