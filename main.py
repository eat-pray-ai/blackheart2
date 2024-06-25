import json

from html2image import Html2Image
from random import choices, choice
from requests import get


vocabularies = {
  "cet4": 7,
  "cet6": 5,
  "tem4": 3,
  "tem8": 1,
  "gmat": 2,
  "gre": 2,
  "ielts": 2,
  "sat": 2,
  "toefl": 2,
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
  word["bookId"] = vocab
  return word


def clean_word(word: dict) -> dict:
  cleaned = { "word": word["wordHead"], "type": word["bookId"] }
  content = word["content"]
  if "trans" in content:
    cleaned["definition"] = {}
    for tran in content["trans"]:
      pos = tran["pos"] if "pos" in tran else ""
      tran_cn = tran["tranCn"] if "tranCn" in tran else ""
      tran_other = tran["tranOther"] if "tranOther" in tran else ""
      cleaned["definition"][f"{pos} {tran_cn}"] = tran_other

  if "relWord" in content:
    cleaned["conjugate"] = {}
    for rel in content["relWord"]["rels"]:
      pos = rel["pos"] if "pos" in rel else ""
      rel_words = []
      for word in rel["words"]:
        hwd = word["hwd"] if "hwd" in word else ""
        tran = word["tran"] if "tran" in word else ""
        rel_words.append(f"{hwd}: {tran}")

      cleaned["conjugate"][pos] = rel_words

  if "syno" in content:
    cleaned["synonym"] = {}
    for syn in content["syno"]["synos"]:
      pos = syn["pos"] if "pos" in syn else ""
      tran = syn["tran"] if "tran" in syn else ""
      hwds = []
      for hwd in syn["hwds"]:
        if type(hwd) == str:
          hwds.append(hwd)
        else:
          hwds.append(hwd["w"])
      cleaned["synonym"][f"{pos} {tran}"] = hwds

  if "sentence" in content:
    cleaned["example"] = {}
    for ex in content["sentence"]["sentences"]:
      s_content = ex["sContent"] if "sContent" in ex else ""
      s_cn = ex["sCn"] if "sCn" in ex else ""
      cleaned["example"][s_content] = s_cn

  try:
    quote = get("https://apiv3.shanbay.com/weapps/dailyquote/quote/").json()
    cleaned["quote"] = {quote["content"]: quote["translation"]}
  except e:
    print(e)

  return cleaned


def definition(word: dict) -> str:
  if "definition" not in word:
    return ""

  result = []
  template = "<li>{}<br />{}</li>"
  for k, v in word["definition"].items():
    result.append(template.format(k, v))

  return f"""
    <h2>Definition 释义</h2>
    <ul id="definition">
      {chr(10).join(result)}
    </ul>
  """


def conjugate(word: dict) -> str:
  if "conjugate" not in word:
    return ""

  result = []
  template = """<li>{}<span />{}</li>"""
  for k, v in word["conjugate"].items():
    result.append(template.format(k, "<br />".join(v)))

  return f"""
    <h2>Conjugate 同根词</h2>
    <ul id="conjugate">
      {chr(10).join(result)}
    </ul>
  """


def synonym(word: dict) -> str:
  if "synonym" not in word:
    return ""

  result = []
  template = "<li>{}<br />{}</li>"
  for k, v in word["synonym"].items():
    result.append(template.format(k, "; ".join(v)))

  return f"""
    <h2>Synonym 近义词</h2>
    <ul id="synonym">
      {chr(10).join(result)}
    </ul>
  """


def example(word: dict) -> str:
  if "example" not in word:
    return ""

  result = []
  template = "<li>{}<br />{}</li>"
  for k, v in word["example"].items():
    result.append(template.format(k, v))

  return f"""
    <h2>Example 例句</h2>
    <ol id="example">
      {chr(10).join(result)}
    </ol>
  """


def quote(word: dict) -> str:
  if "quote" not in word:
    return ""

  result = []
  template = "<p>{}</p>"
  for k, v in word["quote"].items():
    result.append(template.format(k))
    result.append(template.format(v))
  return f"""
    <h2>Daily Quote 每日一句</h2>
    {chr(10).join(result)}
  """


hti = Html2Image(size=(540, 960))
with open("./template.html", "r") as f:
  html = f.read()

word = clean_word(raw_word())

try:
  html = (html.replace("{{ word }}", word["word"])
              .replace("{{ definition }}", definition(word))
              .replace("{{ conjugate }}", conjugate(word))
              .replace("{{ synonym }}", synonym(word))
              .replace("{{ example }}", example(word))
              .replace("{{ quote }}", quote(word))
          )
  hti.screenshot(
    html_str=html,
    save_as=f"{word['word']}.{word['type']}.png"
  )
except Exception as e:
  print(word)
  raise e
