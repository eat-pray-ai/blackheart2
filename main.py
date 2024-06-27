from html2image import Html2Image
from utils.clean import raw_word, clean_word

ids: list[str] = []


def definition(word: dict) -> str:
  if "definition" not in word:
    return ""

  result = []
  template = "<li id={}>{}<br />{}</li>"
  for pos, cn, en in word["definition"]:
    ids.append(f"{cn} {en}")
    result.append(template.format(f"{cn} {en}", f"{pos} {cn}", en))

  return f"""
    <h2>Definition 释义</h2>
    <ul id="definition" style="font-size: large;">
      {chr(10).join(result)}
    </ul>
  """


def conjugate(word: dict) -> str:
  if "conjugate" not in word:
    return ""

  result = []
  template = """<li id={}>{}</li>"""
  for pos, cn, en in word["conjugate"]:
    ids.append(f"{en} {cn}")
    result.append(template.format(f"{en} {cn}", f"{pos} {en}: {cn}"))

  return f"""
    <h2>Conjugate 同根词</h2>
    <ul id="conjugate" style="font-size: large;">
      {chr(10).join(result)}
    </ul>
  """


def synonym(word: dict) -> str:
  if "synonym" not in word:
    return ""

  result = []
  template = "<li id={}>{}</li>"
  for pos, cn, en in word["synonym"]:
    ids.append(f"{cn} {en}")
    result.append(template.format(f"{cn} {en}", f"{pos} {cn}: {en}"))

  return f"""
    <h2>Synonym 近义词</h2>
    <ul id="synonym" style="font-size: large;">
      {chr(10).join(result)}
    </ul>
  """


def example(word: dict) -> str:
  if "example" not in word:
    return ""

  result = []
  template = "<li id={}>{}<br />{}</li>"
  for cn, en in word["example"]:
    ids.append(f"{en} {cn}")
    result.append(template.format(f"{en} {cn}", en, cn))

  return f"""
    <h2>Example 例句</h2>
    <ol id="example" style="font-size: large; font-style: italic;">
      {chr(10).join(result)}
    </ol>
  """


def quote(word: dict) -> str:
  if "quote" not in word:
    return ""

  result = []
  template = "<p id={}>{}</p>"
  for en, cn in word["quote"].items():
    ids.append(en)
    ids.append(cn)
    result.append(template.format(en, en))
    result.append(template.format(cn, cn))
  return f"""
    <h2>Daily Quote 每日一句</h2>
    {chr(10).join(result)}
  """

custom_flags=[
  "--no-sandbox",
  "--disable-gpu",
  "--default-background-color=000000",
  "--hide-scrollbars",
  "--enable-features=ConversionMeasurement,AttributionReportingCrossAppWeb",
  ]
hti = Html2Image(size=(540, 960), custom_flags=custom_flags)
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
