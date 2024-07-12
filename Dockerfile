FROM python:3.10-slim-bookworm

WORKDIR /blackheart2

RUN apt-get update && apt-get install -y \
  jq wget chromium fonts-noto-cjk fonts-noto-color-emoji \
  && wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq \
  && chmod +x /usr/bin/yq \
  && rm -rf /var/lib/apt/lists/* \
  && pip install pipenv

COPY . .
RUN pipenv sync -d
#ENTRYPOINT [ "/blackheart2/entrypoint.sh" ]
