import json

from html2image import Html2Image
from random import choice
from requests import get


def trans(word: dict) -> str:
    result = []
    template = "<li><span style='font-style:bold;'>{}</span> {}<br />{}</li>"
    for tr in word["content"]["trans"]:
        result.append(
            template.format(tr["pos"], tr["tranCn"], tr["tranOther"])
        )
    return "\n".join(result)


def conjugate(word: dict) -> str:
    result = []
    template = "<li>{}<br />{}</li>"
    for cj in word["content"]["relWord"]["rels"]:
        cj_words = []
        for cj_word in cj["words"]:
            cj_words.append(f"{cj_word['hwd']}: {cj_word['tran']}")
        result.append(template.format(cj["pos"], "<br />".join(cj_words)))
    return "\n".join(result)


def example(word: dict) -> str:
    result = []
    template = "<li>{}<br />{}</li>"
    for ex in word["content"]["sentence"]["sentences"]:
        result.append(template.format(ex["sContent"], ex["sCn"]))
    return "\n".join(result)


hti = Html2Image(size=(540, 960))
with open("./template.html", "r") as f:
    html = f.read()

with open("./cet4.json", "r") as f:
    words = json.load(f)

word = choice(words)["content"]["word"]
today_quote = get("https://apiv3.shanbay.com/weapps/dailyquote/quote/").json()

try:
    html = (html.replace("{{ word }}", word["wordHead"])
                .replace("{{ trans }}", trans(word))
                .replace("{{ conjugate }}", conjugate(word))
                .replace("{{ example }}", example(word))
                .replace("{{ content }}", today_quote["content"])
                .replace("{{ translation }}", today_quote["translation"])
            )
except Exception as e:
    print(word)
    print(e)

hti.screenshot(html_str=html, save_as="word.png")
