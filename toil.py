from holmes import *
import json
from subprocess import (Popen, PIPE)
import socket

bapd = "bapd"
bapProc = Popen([bapd], stdout=PIPE)
addr = bapProc.stdout.readline()
sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
sock.connect('/tmp/bapd')

class ToIL():
  premises = [Premise("arch", [Bind("fileName", "string")
                              ,Bind("arch",     "string")])
             ,Premise("reachable", [Bind("fileName", "string")
                                   ,Bind("addr",     "addr")])
             ,Premise("word128",   [Bind("fileName", "string")
                                   ,Bind("addr",     "addr")
                                   ,Bind("data",     "blob")])]
  conclusions = [ConcTy("hasil", ["string", "addr", "json"]),
                 ConcTy("fallthrough", ["string", "addr", "addr"]),
                 ConcTy("hasasm", ["string", "addr", "string"])]
  name = "ToIL"
  def analyze(self, fileName, arch, addr, data):
    c = chr(0)
    if (arch == 'x86'):
      c = chr(0)
    if (arch == 'x86_64'):
      c = chr(1)
    if (arch == 'arm'):
      c = chr(2)
    encAddr = "{0:0{1}x}".format(addr,16)
    data = data.ljust(16, '\0'.encode())
    pay = c.encode() + data + encAddr.encode()
    sock.send(c.encode() + data + encAddr.encode())
    s = sock.recv(65536).decode()
    try:
      out,pos = json.JSONDecoder().raw_decode(s)
      rest = s[pos+1:].split('\n')
      if rest[0] == "None":
        asm = []
      else:
        asm = [Conc("hasasm", [fileName, addr, rest[0]])]
      fall = int(rest[1].split(':')[0])
      return [Conc("hasil", [fileName, addr, out]),
              Conc("fallthrough", [fileName, addr, fall])] + asm
    except ValueError:
      print(s)
      print("No IL")
      return []
