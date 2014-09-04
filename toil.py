from holmes import *
import json
from subprocess import (Popen, PIPE)

toil = "/home/maurer/Sources/bap-lifter/toil.native"

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
    toilProc = Popen([toil, '--arch', arch, '--addr', str(addr),'--format' , 'json', '--dump-asm', '--dump-fallthrough'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    toilProc.stdin.write(data)
    toilProc.stdin.close()
    s = toilProc.stdout.read().decode()
    try:
      out,pos = json.JSONDecoder().raw_decode(s)
      rest = s[pos+1:].split('\n')
      if rest[0] == "Assembly not available for this architecture.":
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
