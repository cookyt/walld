#!/usr/bin/env python3
import subprocess

class FehBackgroundSetter(object):
  """ Class for setting the background. Uses the program `feh' to do this."""

  def __init__(self):
    kScaleDescription = (
      "The style used to size the image. Supported values are:\n" +
      "\t+ center\n" +
      "\t+ fill\n" +
      "\t+ max\n" +
      "\t+ scale\n" +
      "\t+ tile\n" +
      "See the feh man page for info on what each mean."
    )

    def _ValidateStyle(style):
      valid_styles = {"center", "fill", "max", "scale", "tile"}
      return (style in valid_styles);

    self.config = {
      "image_style" : ("scale", kScaleDescription, _ValidateStyle)
    }

  def Set(self, filepath):
    """ Sets the background to the given file. Returns True if the command
    succeeds.
      filepath: The background file to use. Can be any of the image types
                supported by `feh', use a full-path.
    """
    return (subprocess.call(["feh", "--bg-" + self.config["image_style"][0],
                            "--no-fehbg", filepath]) == 0)
