#!/bin/bash -l

cd "$(dirname "$0")" || exit

pipenv run python main.py
file=$(ls "$GITHUB_WORKSPACE"/*.mp4)
title=$(basename "$file" | cut -d'.' -f1)
tag=$(echo "$title" | cut -d'-' -f2)
echo "title=$title" >> "$GITHUB_OUTPUT"
echo "tag=$tag" >> "$GITHUB_OUTPUT"
