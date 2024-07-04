FROM python:3.10-slim-bookworm

WORKDIR /blackheart2

RUN apt-get update && apt-get install -y \
  git chromium fonts-noto-cjk fonts-noto-color-emoji \
  && rm -rf /var/lib/apt/lists/* \
  && pip install pipenv

COPY . .
RUN pipenv sync -d
#ENTRYPOINT [ "/blackheart2/entrypoint.sh" ]
