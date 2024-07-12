# curl -L \
# -H "Accept: application/vnd.github+json" \
# -H "Authorization: Bearer <YOUR-TOKEN>" \
# -H "X-GitHub-Api-Version: 2022-11-28" \
#   https://api.github.com/repos/OWNER/REPO/actions/secrets/public-key

import os
import sys

import requests
from base64 import b64encode
from nacl import encoding, public

repo = os.environ.get("GITHUB_REPOSITORY")


def get_key(github_token: str) -> dict:
  headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {github_token}",
    "X-GitHub-Api-Version": "2022-11-28",
  }

  url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
  return requests.get(url, headers=headers).json()


def encrypt(public_key: str, secret_value: str) -> str:
  public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
  sealed_box = public.SealedBox(public_key)
  encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
  return b64encode(encrypted).decode("utf-8")


def update_secret(github_token: str, secret: dict, key_id: str) -> int:
  headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {github_token}",
    "X-GitHub-Api-Version": "2022-11-28",
  }

  url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret['name']}"
  body = {
    "encrypted_value": secret["value"],
    "key_id": key_id,
  }
  return requests.put(url, headers=headers, json=body).status_code


def main():
  github_token = os.environ.get("GH_TOKEN")
  key = get_key(github_token)
  print(key)

  with open("./youtube.token.b64", "r", encoding="utf-8") as f:
    youtube_token = f.read()

  encrypted = encrypt(key["key"], youtube_token)
  secret = {
    "name": "YOUTUBE_TOKEN",
    "value": encrypted,
  }
  update_secret(github_token, secret, key["key_id"])


if __name__ == "__main__":
  sys.exit(main())
