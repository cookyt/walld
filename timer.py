#!/usr/bin/env python3
import random
import time

class GaussianRandomTimer:
  def __init__(self):
    kAvgTimeSecondsDescription = ("The mean time in seconds between events. " + 
                                  "Set to 0 to disable all time-based events.")
    kTimeRangeSecondsDescription = ("The maximum time in seconds from the " + 
        "mean an even can take. Corresponds to three standard deviations " +
        "from the above mean")

    noop = lambda: True
    self.config = {
      "avg_time_seconds"   : ("600", kAvgTimeSecondsDescription,   noop),
      "time_range_seconds" : ("300", kTimeRangeSecondsDescription, noop)
    }

    self.time_interval = 0
    self.last_call = 0

  def Reset(self):
    """ Resets the timer and returns the new time interval to wait. """
    self.time_interval = self._GaussianRandomTime()
    self.last_call = time.time()
    return self.time_interval

  def Remaining(self):
    """ Returns the remaining time since the last call to Reset() """
    time_passed = (time.time() - self.last_call)
    return self.time_interval - time_passed

  def RemainingOrReset(self):
    """ Returns the remaining time or resets the clock if the time is up """
    time_left = self.Remaining()
    if time_left <= 0:
      time_left = self.Reset()
    return time_left

  def Enabled(self):
    return (int(self.config["avg_time_seconds"][0]) != 0)

  def _GaussianRandomTime(self):
    avg_time = float(self.config["avg_time_seconds"][0])
    max_range = float(self.config["time_range_seconds"][0])

    if max_range == 0:
      # Don't bother with the math
      return int(avg_time)
    else:
      # 96% of numbers in a gaussian are within 3 stddevs of the mean
      stddev = max_range/3.

      # Get a number in a loop to prevent that 4% from occuring
      while True:
        num = random.gauss(avg_time, stddev)
        if avg_time - max_range < num < avg_time + max_range:
          return int(num)
