import json
from random import choices, choice
from requests import get


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


def raw_word() -> dict:
  vocab = choices(list(vocabularies.keys()), weights=vocabularies.values())[0]
  with open(f"./vocabulary/{vocab}.json", "r") as f:
    try:
      words = json.load(f)
    except json.decoder.JSONDecodeError as e:
      print(f"Error in {vocab}.json")
      raise e

  word = choice(words)["content"]["word"]
  has_definition = int("trans" in word["content"])
  has_conjugate = int("relWord" in word["content"])
  has_synonym = int("syno" in word["content"])
  has_example = int("sentence" in word["content"])
  if has_definition + has_conjugate + has_synonym + has_example <= 2:
    return raw_word()

  word["bookId"] = vocab
  return word


def clean_definition(content: dict) -> list:
  definition = []
  for tran in content["trans"]:
    pos = tran["pos"].strip() if "pos" in tran else ""
    cn = tran["tranCn"].strip() if "tranCn" in tran else ""
    en = tran["tranOther"].strip() if "tranOther" in tran else ""
    definition.append([pos, cn, en])

  return definition


def clean_conjugate(content: dict) -> list:
  conjugate = []
  for rel in content["relWord"]["rels"]:
    pos = rel["pos"].strip() if "pos" in rel else ""
    for word in rel["words"]:
      en = word["hwd"].strip() if "hwd" in word else ""
      cn = word["tran"].strip() if "tran" in word else ""
      conjugate.append([pos, cn, en])

  return conjugate


def clean_synonym(content: dict) -> list:
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

  return synonym


def clean_example(content: dict) -> list:
  example = []
  for ex in content["sentence"]["sentences"]:
    en = ex["sContent"].strip() if "sContent" in ex else ""
    cn = ex["sCn"].strip() if "sCn" in ex else ""
    example.append([cn, en])

  return example


def clean_word(word: dict) -> dict:
  cleaned = {"word": word["wordHead"], "type": word["bookId"]}
  content = word["content"]
  if "trans" in content:
    cleaned["definition"] = clean_definition(content)

  if "relWord" in content:
    cleaned["conjugate"] = clean_conjugate(content)

  if "syno" in content:
    cleaned["synonym"] = clean_synonym(content)

  if "sentence" in content:
    cleaned["example"] = clean_example(content)

  try:
    quote = get("https://apiv3.shanbay.com/weapps/dailyquote/quote/").json()
    cleaned["quote"] = [quote["content"], quote["translation"]]
  except Exception as e:
    print(e)

  return cleaned


if __name__ == "__main__":
  word = clean_word(raw_word())
  print(json.dumps(word, ensure_ascii=False, indent=2))
