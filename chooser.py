#!/usr/bin/env python3
import os
import random

class RandomDirectoryBackground(object):
  """ Sets backgrounds randomly from a directory. Rescans the directory on
  wakeup."""

  """ Dictionary of configurable options.
  key:String, val:(value:String, description:String,
                   validate:Function(String)->Bool)

  where key is the externally-visible variable name
        value is the current value of the variable
        description is a string describing what the variable does and what a
          valid value should look like
        validator is a function which validates the value
  """

  def __init__(self):
    self.config = {
      "directory"          : ("/home/carlos/pics/wall/", "", lambda: True),
    }
    self.current_wallpaper_ = ""

  def Next(self):
    files = os.listdir(self.config["directory"][0])
    next_wallpaper = self.current_wallpaper_
    while next_wallpaper == self.current_wallpaper_:
      next_wallpaper = random.choice(files)
    self.current_wallpaper_ = next_wallpaper

    return self.Current()

  def Current(self):
    return self.config["directory"][0] + self.current_wallpaper_
