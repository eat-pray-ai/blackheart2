import cv2
import asyncio
import numpy as np
from html2image import Html2Image
from edge_tts import Communicate
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
from utils.clean import raw_word, clean_word

ids: list = []
custom_flags=[
  "--no-sandbox",
  "--disable-gpu",
  "--default-background-color=000000",
  "--hide-scrollbars",
  "--enable-features=ConversionMeasurement,AttributionReportingCrossAppWeb",
  ]
hti = Html2Image(size=(540, 960), custom_flags=custom_flags)
voices = ["zh-CN-XiaoxiaoNeural", "en-GB-LibbyNeural"]


def definition(word: dict) -> str:
  if "definition" not in word:
    return ""

  result = []
  template = "<li id={}>{}<br />{}</li>"
  ids.append(["definition", "", 1, 0])
  for pos, cn, en in word["definition"]:
    ids.append([cn, en, 0, 1])
    result.append(template.format(cn, f"{pos} {cn}", en))

  return f"""
    <h2 id="definition">Definition 释义</h2>
    <ul style="font-size: large;">
      {chr(10).join(result)}
    </ul>
  """


def conjugate(word: dict) -> str:
  if "conjugate" not in word:
    return ""

  result = []
  template = """<li id={}>{}</li>"""
  ids.append(["conjugate", "", 1, 0])
  for pos, cn, en in word["conjugate"]:
    ids.append([en, cn, 1, 0])
    result.append(template.format(en, f"{pos} {en}: {cn}"))

  return f"""
    <h2 id="conjugate">Conjugate 同根词</h2>
    <ul style="font-size: large;">
      {chr(10).join(result)}
    </ul>
  """


def synonym(word: dict) -> str:
  if "synonym" not in word:
    return ""

  result = []
  template = "<li id={}>{}</li>"
  ids.append(["synonym", "", 1, 0])
  for pos, cn, en in word["synonym"]:
    ids.append([cn, en, 0, 1])
    result.append(template.format(cn, f"{pos} {cn}: {en}"))

  return f"""
    <h2 id="synonym">Synonym 近义词</h2>
    <ul style="font-size: large;">
      {chr(10).join(result)}
    </ul>
  """


def example(word: dict) -> str:
  if "example" not in word:
    return ""

  result = []
  template = "<li id={}>{}<br />{}</li>"
  ids.append(["example", "", 1, 0])
  for cn, en in word["example"]:
    ids.append([en, cn, 1, 0])
    result.append(template.format(en, en, cn))

  return f"""
    <h2 id="example">Example 例句</h2>
    <ol style="font-size: large; font-style: italic;">
      {chr(10).join(result)}
    </ol>
  """


def quote(word: dict) -> str:
  if "quote" not in word:
    return ""

  result = []
  template = "<p id={}>{}</p>"
  ids.append(["daily quote", "", 1, 0])
  for en, cn in word["quote"].items():
    ids.append([en, cn, 1, 0])
    result.append(template.format(en, en))
    result.append(template.format(en, cn))
  return f"""
    <h2 id="daily quote">Daily Quote 每日一句</h2>
    {chr(10).join(result)}
  """


def init():
  word = clean_word(raw_word())
  ids.append([word["word"], "", 1, 0])
  with open("./template.html", "r") as f:
    html = f.read()
  html = (html.replace("{{ word }}", word["word"])
              .replace("{{ definition }}", definition(word))
              .replace("{{ conjugate }}", conjugate(word))
              .replace("{{ synonym }}", synonym(word))
              .replace("{{ example }}", example(word))
              .replace("{{ quote }}", quote(word))
          )
  return word, html


async def video(word: dict, html: str):
  videos = []
  for i, id in enumerate(ids):
    hti.screenshot(
      html_str=html,
      css_str=f"#{id[0]} {{ font-weight: bold; }}",
      save_as=f"{word['word']}-{i}.png"
    )

    audios = []
    if id[0] != "":
      communicate = Communicate(id[0], voices[id[2]])
      await communicate.save(f"{word['word']}-{0}.mp3")
      audios.append(AudioFileClip(f"{word['word']}-{0}.mp3"))
    if id[1] != "":
      communicate = Communicate(id[1], voices[id[3]])
      await communicate.save(f"{word['word']}-{1}.mp3")
      audios.append(AudioFileClip(f"{word['word']}-{1}.mp3"))

    image = cv2.imread(f"{word['word']}-{i}.png")
    audio_clip = concatenate_audioclips(audios)
    duration = audio_clip.duration
    video_writer = cv2.VideoWriter(
      f"{word['word']}-{i}.mp4",
      cv2.VideoWriter_fourcc(*"mp4v"),
      1,
      (image.shape[1], image.shape[0])
    )

    for _ in range(np.ceil(duration).astype(int)):
      video_writer.write(image)
    video_writer.release()
    video_clip = VideoFileClip(f"{word['word']}-{i}.mp4")
    video_audio = video_clip.set_audio(audio_clip)
    videos.append(video_audio)

  concatenate_videoclips(videos).write_videofile(f"{word['word']}-{word['type']}.mp4")


if __name__ == "__main__":
  word, html = init()
  asyncio.run(video(word, html))
  print("Done!")
