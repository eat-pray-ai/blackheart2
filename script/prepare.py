import asyncio
import json
from random import choices, choice

import aiofiles
import aiohttp
from edge_tts import Communicate
# from base64 import urlsafe_b64encode
from hashlib import md5


voices = ["zh-CN-XiaoxiaoNeural", "en-GB-LibbyNeural"]
vocabularies: dict[str, int] = {
  "CET4": 7,
  "CET6": 5,
  "TEM4": 3,
  "TEM8": 1,
  "GMAT": 2,
  "GRE": 2,
  "IELTS": 2,
  "SAT": 2,
  "TOEFL": 2,
}


async def save_audio(contents_voices: list[tuple[str, str]]):
  for content, voice in contents_voices:
    commu = Communicate(content, voice)
    await commu.save(f"public/{md5(content.encode()).hexdigest()}.mp3")


async def get_raw_word() -> dict:
  vocab = choices(list(vocabularies.keys()), weights=vocabularies.values())[0]
  try:
    async with aiofiles.open(f"vocabulary/{vocab}.json", "r", encoding="utf8") as f:
      content = await f.read()
  except json.decoder.JSONDecodeError as e:
    print(f"Error in {vocab}.json")
    raise e

  words = json.loads(content)
  word = choice(words)["content"]["word"]
  has_definition = int("trans" in word["content"])
  has_conjugate = int("relWord" in word["content"])
  has_synonym = int("syno" in word["content"])
  has_example = int("sentence" in word["content"])
  if has_definition + has_conjugate + has_synonym + has_example <= 2:
    return await get_raw_word()

  word["bookId"] = vocab
  return word


async def clean_definition(content: dict) -> list:
  definition = []
  for tran in content["trans"]:
    pos = tran["pos"].strip() if "pos" in tran else ""
    cn = tran["tranCn"].strip() if "tranCn" in tran else ""
    en = tran["tranOther"].strip() if "tranOther" in tran else ""
    definition.append([pos, cn, en])
    await save_audio([(cn, voices[0]), (en, voices[1])])

  return definition


async def clean_conjugate(content: dict) -> list:
  conjugate = []
  for rel in content["relWord"]["rels"]:
    pos = rel["pos"].strip() if "pos" in rel else ""
    for word in rel["words"]:
      en = word["hwd"].strip() if "hwd" in word else ""
      cn = word["tran"].strip() if "tran" in word else ""
      conjugate.append([pos, cn, en])
      await save_audio([(cn, voices[0]), (en, voices[1])])

  return conjugate


async def clean_synonym(content: dict) -> list:
  synonym = []
  for syn in content["syno"]["synos"]:
    pos = syn["pos"].strip() if "pos" in syn else ""
    cn = syn["tran"].strip() if "tran" in syn else ""
    en = []
    for hwd in syn["hwds"]:
      if isinstance(hwd, str):
        en.append(hwd.strip())
      else:
        en.append(hwd["w"].strip())

    synonym.append([pos, cn, "; ".join(en)])
    await save_audio([(cn, voices[0]), ("; ".join(en), voices[1])])

  return synonym


async def clean_example(content: dict) -> list:
  example = []
  for ex in content["sentence"]["sentences"]:
    en = ex["sContent"].strip() if "sContent" in ex else ""
    cn = ex["sCn"].strip() if "sCn" in ex else ""
    example.append([cn, en])
    await save_audio([(cn, voices[0]), (en, voices[1])])

  return example


async def clean_word(word: dict) -> dict:
  cleaned = {"word": word["wordHead"], "type": word["bookId"]}
  await save_audio([(cleaned["word"], voices[1])])

  content = word["content"]
  if "trans" in content:
    cleaned["definition"] = await clean_definition(content)

  if "relWord" in content:
    cleaned["conjugate"] = await clean_conjugate(content)

  if "syno" in content:
    cleaned["synonym"] = await clean_synonym(content)

  if "sentence" in content:
    cleaned["example"] = await clean_example(content)

  try:
    async with aiohttp.ClientSession(trust_env=True) as session:
      async with session.get("https://apiv3.shanbay.com/weapps/dailyquote/quote/") as resp:
        quote = await resp.json()
        cn = quote["translation"]
        en = quote["content"]
        cleaned["quote"] = [en, cn]
        await save_audio([(cn, voices[0]), (en, voices[1])])
  except Exception as e:
    print(e)

  return cleaned


async def main():
  raw_word = await get_raw_word()
  chosen_word = await clean_word(raw_word)
  async with aiofiles.open("src/word.json", "w", encoding="utf8") as f:
    await f.write(json.dumps(chosen_word, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  asyncio.run(main())
