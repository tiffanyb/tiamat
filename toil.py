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
  conclusions = [ConcTy("hasil", ["string", "addr", "string"])]
  name = "ToIL"
  def analyze(self, fileName, arch, addr, data):
    toilProc = Popen([toil, '--arch', arch, '--addr', str(addr),'--format' , 'json'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    toilProc.stdin.write(data)
    toilProc.stdin.close()
    jstr = toilProc.stdout.read().decode()
    try:
      out = json.loads(jstr)
      return [Conc("hasil", [fileName, addr, jstr])]
    except ValueError:
      print("No IL")
      print(ctx)
      print(jstr)
      return []
