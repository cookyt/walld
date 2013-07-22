WallD(aemon)
============

This daemon periodically changes your background to a random background chosen
from a directory. It watches the directory so that new images still have a
chance of being shown.

The `walldo` script that comes with it sends commands to it asyncronously. The
daemon supports the following commands:

+ walldo next
  + Tells the daemon to pick a new wallpaper immediately and restart the
    countdown timer until the next wallpaper.
+ walldo refresh
  + Re-applies the current wallpaper
+ walldo var
  + Lists the configureable variables
+ walldo var <varname>
  + Gives more specific information about the given named variable
+ walldo var <varname> <newval>
  + Sets the variable to the new given value
