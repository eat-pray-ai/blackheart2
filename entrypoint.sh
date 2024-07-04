#!/bin/bash -l

cd "$(dirname "$0")" || exit

pipenv run python main.py
file=$(ls /github/workspace/*.mp4)
title=$(basename "$file" | cut -d'.' -f1)
tag=$(basename "$file" | cut -d'-' -f2)
echo "title=$title" >> "$GITHUB_OUTPUT"
echo "tag=$tag" >> "$GITHUB_OUTPUT"
