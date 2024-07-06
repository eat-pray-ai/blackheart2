#!/bin/bash -l

cd "$(dirname "$0")" || exit

pipenv run python main.py
file=$(ls "$GITHUB_WORKSPACE"/*.mp4)
title=$(basename "$file" | cut -d'.' -f1)
word=$(echo "$title" | cut -d'-' -f1)
tag=$(echo "$title" | cut -d'-' -f2)
playlistId=$(echo "$YOUTUBE_PLAYLISTS" | jq -r ".$tag")

description=$(cat <<-EOM
Keep learning with me 🌱
${word} is a important word in ${tag}, grasp it to make yourself one step further! 🤓
Your subscription and thumb up👍 are my motivation to create more content 🤗

The video's generation is AI🤖 POWERED! Wanna create your own video?
Check out my Github project 🚀: https://github.com/eat-pray-ai/yutu
EOM
)

{
  echo "title=$title"
  echo "tag=$tag"
  echo "playlistId=$playlistId"
  echo "description<<EOV"
  echo "$description"
  echo "EOV"
} >> "$GITHUB_OUTPUT"
