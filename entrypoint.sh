#!/bin/bash -l

cd $(dirname $0)

pipenv run python main.py
file=$(ls ./utils/*.mp4)
echo "file=$file" >> $GITHUB_OUTPUT
