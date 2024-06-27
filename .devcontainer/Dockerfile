FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y \
  git chromium fonts-noto-cjk fonts-noto-color-emoji \
  && rm -rf /var/lib/apt/lists/* \
  && pip install pipenv
