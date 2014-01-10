#!/usr/bin/env python3
import subprocess

class ImageMagickImageDarkener(object):
  """ Class darkens the image and saves the darkened copy in the tmp_file_name
  denoted by its config dictionary.
  """

  def __init__(self):
    noop = lambda: True
    self.config = {
      "darken_percent"     : ("0%",                  "",  noop),
      "tmp_file_name"      : ("/tmp/background.jpg", "",  noop),
    }

  def Process(self, filepath):
    subprocess.call(["convert", filepath, "-fill", "black", "-colorize",
                     self.config["darken_percent"][0],
                     self.config["tmp_file_name"][0]])
  def TmpFile(self):
    return self.config["tmp_file_name"][0]
