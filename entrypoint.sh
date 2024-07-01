#!/bin/bash -l

cd $(dirname $0)

pipenv run python main.py
file=$(ls /github/workspace/*.mp4)
echo "title=$(basename $file | cut -d'.' -f1)" >> $GITHUB_OUTPUT
