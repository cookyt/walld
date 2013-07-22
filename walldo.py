#!/usr/bin/env python3
import socket
import sys

err = sys.stderr.write

kAddress = '127.0.0.1'
kBufferSize = 1024

# TODO do something to pass port number from server instance to client
kPort = 9999

def main():
  if len(sys.argv) < 2:
    err("Expected a command\n")
    sys.exit(1)

  command = bytearray(" ".join(sys.argv[1:]), "UTF-8")
  if len(command) > kBufferSize:
    err("Command too large\n")
    sys.exit(1)

  com_line = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  com_line.connect((kAddress, kPort))
  com_line.send(command)

  response = com_line.recv(kBufferSize)
  com_line.close()

  print("Response: " + response.decode())

if __name__ == '__main__':
  main()
