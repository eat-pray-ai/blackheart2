import os
import cv2
import asyncio
from json import loads
from textwrap import dedent
from html2image import Html2Image
from edge_tts import Communicate
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
from utils.clean import raw_word, clean_word

ids: list = []
custom_flags = [
  "--no-sandbox",
  "--disable-gpu",
  "--default-background-color=000000",
  "--hide-scrollbars",
  "--enable-features=ConversionMeasurement,AttributionReportingCrossAppWeb",
  ]
hti = Html2Image(size=(540, 960), custom_flags=custom_flags, disable_logging=True)
voices = ["zh-CN-XiaoxiaoNeural", "en-GB-LibbyNeural"]


def definition(word: dict) -> str:
  if "definition" not in word:
    return ""

  result = []
  template = """<li id="{}">{}<br />{}</li>"""
  ids.append([f"definition", "definition", "", 1, 0])
  for pos, cn, en in word["definition"]:
    iid = f"definition-{len(result)}"
    ids.append([iid, cn, en, 0, 1])
    result.append(template.format(iid, f"{pos} {cn}", en))

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
  template = """<li id="{}">{}</li>"""
  ids.append(["conjugate", "conjugate", "", 1, 0])
  for pos, cn, en in word["conjugate"]:
    iid = f"conjugate-{len(result)}"
    ids.append([iid, en, cn, 1, 0])
    result.append(template.format(iid, f"{pos} {en}: {cn}"))

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
  template = """<li id="{}">{}</li>"""
  ids.append(["synonym", "synonym", "", 1, 0])
  for pos, cn, en in word["synonym"]:
    iid = f"synonym-{len(result)}"
    ids.append([iid, cn, en, 0, 1])
    result.append(template.format(iid, f"{pos} {cn}: {en}"))

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
  template = """<li id="{}">{}<br />{}</li>"""
  ids.append(["example", "example", "", 1, 0])
  for cn, en in word["example"]:
    iid = f"example-{len(result)}"
    ids.append([iid, en, cn, 1, 0])
    result.append(template.format(iid, en, cn))

  return f"""
    <h2 id="example">Example 例句</h2>
    <ol style="font-size: large;">
      {chr(10).join(result)}
    </ol>
  """


def quote(word: dict) -> str:
  if "quote" not in word:
    return ""

  result = []
  template = """<p id="{}">{}</p>"""
  ids.append(["daily_quote", "daily quote", "", 1, 0])

  en, cn = word["quote"]
  ids.append(["daily_quote-0", en, "", 1, 0])
  ids.append(["daily_quote-1", cn, "", 0, 1])
  result.append(template.format("daily_quote-0", en))
  result.append(template.format("daily_quote-1", cn))

  return f"""
    <h2 id="daily_quote">Daily Quote 每日一句</h2>
    {chr(10).join(result)}
  """


def init():
  word = clean_word(raw_word())
  ids.append(["word", word["word"], "", 1, 0])
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
  for i, iid in enumerate(ids):
    hti.screenshot(
      html_str=html,
      css_str=f"#{iid[0]} {{ font-weight: bold; }}",
      save_as=f"{word['word']}-{i}.png"
    )

    audios = []
    if iid[1] != "":
      communicate = Communicate(iid[1], voices[iid[3]])
      await communicate.save(f"{word['word']}-{i}-0.mp3")
      audios.append(AudioFileClip(f"{word['word']}-{i}-0.mp3"))
    if iid[2] != "":
      communicate = Communicate(iid[2], voices[iid[4]])
      await communicate.save(f"{word['word']}-{i}-1.mp3")
      audios.append(AudioFileClip(f"{word['word']}-{i}-1.mp3"))

    image = cv2.imread(f"{word['word']}-{i}.png")
    audio_clip = concatenate_audioclips(audios)
    duration = audio_clip.duration
    video_writer = cv2.VideoWriter(
      f"{word['word']}-{i}.mp4",
      cv2.VideoWriter_fourcc(*"mp4v"),
      1,
      (image.shape[1], image.shape[0])
    )

    for _ in range(int(duration) + 1):
      video_writer.write(image)
    video_writer.release()
    video_clip = VideoFileClip(f"{word['word']}-{i}.mp4")
    video_audio = video_clip.subclip(0, duration).set_audio(audio_clip)
    videos.append(video_audio)

  out = os.environ.get("GITHUB_WORKSPACE", ".")
  concatenate_videoclips(videos).write_videofile(f"{out}/{word['word']}-{word['type']}.mp4")


def output(word: dict):
  title = f"{word['word']}-{word['type']}"
  tag = word["type"]
  playlist_id = loads(os.environ.get("YOUTUBE_PLAYLISTS"))[tag]
  description = dedent(f"""\
    Keep learning with me 🌱
    {word['word']} is a important word in {tag}, grasp it to make yourself one step further! 🤓
    Your subscription and thumb up👍 are my motivation to create more content 🤗
  """)
  comment = dedent(f"""\
    The video's generation is AI🤖 POWERED! Wanna create your own video?
    Check out my Github project 🚀: https://github.com/eat-pray-ai/yutu
  """)

  with open(os.environ.get("GITHUB_OUTPUT"), "a", encoding="utf-8") as f:
    f.write(f"title={title}\n")
    f.write(f"tag={tag}\n")
    f.write(f"playlistId={playlist_id}\n")
    f.write(f"comment<<EOC\n{comment}\nEOC\n")
    f.write(f"description<<EOD\n{description}\nEOD")


if __name__ == "__main__":
  word, html = init()
  asyncio.run(video(word, html))
  output(word)
  print("Done!")
