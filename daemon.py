"""Generic linux daemon base class for python 3.x.

Retrived from:
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""

import sys, os, time, atexit, signal, logging

class Daemon:
  """A generic daemon class.

  Usage: subclass the daemon class and override the run() method."""

  def __init__(self, pidfile):
    self.pidfile = pidfile
  
  def daemonize(self):
    """Deamonize class. UNIX double fork mechanism."""

    try: 
      pid = os.fork() 
      if pid > 0:
        # exit first parent
        sys.exit(0) 
    except OSError as err: 
      logging.getLogger('daemon').error('First fork failed: {0}'.format(err))
      sys.exit(1)
  
    # decouple from parent environment
    os.chdir('/') 
    os.setsid() 
    os.umask(0) 
  
    # do second fork
    try: 
      pid = os.fork() 
      if pid > 0:

        # exit from second parent
        sys.exit(0) 
    except OSError as err: 
      logging.getLogger('daemon').error('Second fork failed: {0}'.format(err))
      sys.exit(1) 
  
    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
  
    # write pidfile
    atexit.register(self.delpid)

    pid = str(os.getpid())
    with open(self.pidfile,'w+') as f:
      f.write(pid + '\n')
  
  def delpid(self):
    try:
      os.remove(self.pidfile)
    except IOError as err:
      logging.getLogger('daemon').error('PID could not be removed: {0}'
                                        .format(err))

  def start(self):
    """Start the daemon. Writes out to the PID file, exiting if it already
    exists."""

    # Check for a pidfile to see if the daemon already runs
    try:
      with open(self.pidfile,'r') as pf:
        pid = int(pf.read().strip())
    except IOError:
      pid = None
  
    if pid:
      message = "pid file {0} already exist. Is the daemon already running?\n"
      sys.stderr.write(message.format(self.pidfile))
      sys.exit(1)
    
    # Start the daemon
    self.daemonize()
    self.run()

  def stop(self):
    """Stop the daemon."""

    # Get the pid from the pidfile
    try:
      with open(self.pidfile,'r') as pf:
        pid = int(pf.read().strip())
    except IOError:
      pid = None
  
    if not pid:
      message = "pidfile {0} does not exist. Is the daemon not running?\n"
      sys.stderr.write(message.format(self.pidfile))
      return False # not an error in a restart

    # Try killing the daemon process
    try:
      while True:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.1)
      return True
    except OSError as err:
      e = str(err.args)
      if e.find("No such process") > 0:
        if os.path.exists(self.pidfile):
          os.remove(self.pidfile)
        sys.stderr.write(
            "Pid file exists, but daemon not running. Removed file.\n")
      else:
        sys.stderr.write(str(err.args))
      return False

  def restart(self):
    """Restart the daemon."""
    self.stop()
    self.start()

  def run(self):
    """You should override this method when you subclass Daemon.
    
    It will be called after the process has been daemonized by 
    start() or restart()."""
