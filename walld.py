#!/usr/bin/env python3
import logging
import signal
import socketserver
import sys

import chooser
import daemon
import setter
import timer
import processor

""" Cycles through a new background on a schedule. Randomizes time between
subsequent calls under a gaussian distribution.

Depends on
  feh         - For X-related background-setting stuff
  imagemagick - For image processing
"""

def GetOrNone(items, index):
  return items[index].decode() if len(items) > index else None

class CommandExecutor(object):
  def __init__(self):
    self.chooser_ = chooser.RandomDirectoryBackground()
    self.setter_ = setter.FehBackgroundSetter()
    self.processor_ = processor.ImageMagickImageDarkener()
    self.timer_ = timer.GaussianRandomTimer()
    self.configurable_ = {self.chooser_, self.setter_, self.processor_,
                          self.timer_}
    self.previous_request_ = "next"
    self.log = logging.getLogger('bgd')

  def Run(self, server):
    def StopServer(signum, frame):
      self.log.error("SIGTERM caught")
      raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, StopServer)

    time_reset_commands = {"next"}
    server.handle_timeout = lambda : self._HandleNext(None)
    try:
      self._HandleNext(None)
      while True:
        if self.timer_.Enabled():
          if self.previous_request_ in time_reset_commands:
            server.timeout = self.timer_.Reset()
            self.log.info("time reset to: {0}".format(self.timer_.Remaining()))
          else:
            server.timeout = self.timer_.RemainingOrReset()
            self.log.info("time not reset; left: {0}"
                          .format(self.timer_.Remaining()))
        else:
          server.timeout = None
        server.handle_request()
    except KeyboardInterrupt:
      pass
    self.log.error("Shutting down daemon")
    return True

  def ParseCommand(self, command):
    args = command.split()
    cmd_str = GetOrNone(args, 0)
    commands = {
      "var" : self._HandleVar,
      "next" : self._HandleNext,
      "refresh" : self._HandleRefresh
    }
    self.previous_request_ = cmd_str
    if cmd_str in commands:
      return commands[cmd_str](args)
    else:
      return "error\nInvalid command\n"

  def _HandleNext(self, args):
    return self._SetWallpaper(self.chooser_.Next())

  def _HandleRefresh(self, args):
    return self._SetWallpaper(self.chooser_.Current())

  def _SetWallpaper(self, fname):
    self.log.info("Setting background to: " + fname)
    self.processor_.Process(fname)
    self.setter_.Set(self.processor_.TmpFile())
    return "done\n"

  def _HandleVar(self, args):
    if len(args) == 1:
      return self._AllVarsDescription()
    elif len(args) == 2:
      varname = GetOrNone(args, 1)
      return self._VarDescription(varname)
    else:
      varname = GetOrNone(args, 1)
      new_value = GetOrNone(args, 2)
      return self._SetVar(varname, new_value)

  def _DescriptionsForConfig(self, config):
    ret = ""
    for key in config:
      ret += "{0}={1}\n".format(key, config[key][0])
    return ret

  def _AllVarsDescription(self):
    ret = "done\n"
    for config in self.configurable_:
      ret += self._DescriptionsForConfig(config.config) + "\n"
    return ret

  def _VarDescription(self, name):
    for config_item in self.configurable_:
      config = config_item.config
      if name in config:
        return "done\n{0}={1}\n{2}\n".format(name, config[name][0],
                                             config[name][1])
    return "error\nInvalid parameter name `{0}'\n".format(name)

  def _SetVar(self, name, new_value):
    for config_item in self.configurable_:
      config = config_item.config
      if name in config:
        if config[name][2](new_value):
          config[name] = (new_value, config[name][1], config[name][2])
          return "done\nValue set: {0}={1}\n".format(name, new_value)
        else:
          return "error\nInvalid value `{0}' for `{1}'\n".format(new_value,
                                                                 name)
    return "error\nInvalid parameter name `{0}'\n".format(name)


def CreateHandler(executor):
  class CommandHandler(socketserver.BaseRequestHandler):
    executor_ = executor

    def handle(self):
      if self.client_address[0] != "127.0.0.1":
        return
      command = self.request.recv(1024).strip()
      self.request.sendall(bytearray(self.executor_.ParseCommand(command),
                           "UTF-8"))
  return CommandHandler


kLogFormat = \
  '%(asctime)-15s - %(name)s - %(levelname)s - %(process)s : %(message)s'

# TODO make configureable
kLogFile = '/home/carlos/.walld.log'
kPidFile = '/home/carlos/.walld.pid'
kPort = 9999

class BackgroundDaemon(daemon.Daemon):
  def run(self):
    logging.basicConfig(filename=kLogFile, format=kLogFormat,
                        level=logging.ERROR)
    host, port = "localhost", kPort
    executor = CommandExecutor()
    server = socketserver.TCPServer((host, port), CreateHandler(executor))

    executor.Run(server)

if __name__ == "__main__":
  if len(sys.argv) < 2:
    sys.stderr.write("Error: expected an argument. (try '{0} help')\n"
                     .format(sys.argv[0]))
    sys.exit(1)

  daemon_commands = {}
  def PrintHelp():
    sys.stderr.write("Background daemon.\n" +
      "Daemon process which changes the background based on several\n" +
      "confugurable parameters. Available commands:\n")
    for key in daemon_commands:
      sys.stderr.write("\t{0} - {1}\n".format(key, daemon_commands[key][1]))
    return True

  bgd = BackgroundDaemon(kPidFile)
  daemon_commands = {
    'start':   (bgd.start,   "Forks off and starts the daemon"),
    'nofork':  (bgd.run,     "Runs the daemon without detaching the process"),
    'kill':    (bgd.stop,    "Kills the currently running daemon"),
    'restart': (bgd.restart, "Restarts the currently running daemon"),
    'help':    (PrintHelp,   "Prints this help message")
  }

  if sys.argv[1] in daemon_commands:
    if not daemon_commands[sys.argv[1]][0]():
      sys.exit(1)
  else:
    sys.stderr.write("Error: unexpected command '{0}'\n".format(sys.argv[1]))
    sys.exit(1)
