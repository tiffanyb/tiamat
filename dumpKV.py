from holmes import *
import sys

#TODO make all clauses optional

class DumpKV:
  premises = [Premise("fallthrough", [Bind("fileName", "string")
                                     ,Bind("addr", "addr")
                                     ,Bind("fall", "addr")])
             ,Premise("succ", [Bind("fileName", "string")
                              ,Bind("addr", "addr")
                              ,Forall("succs", "addr")])
             ,Premise("arch", [Bind("fileName", "string")
                              ,Bind("arch", "string")])
             ,Premise("succ", [Bind("fileName", "string")
                              ,Forall("preds", "addr")
                              ,Bind("addr", "addr")])]
  conclusions = []
  name = "DumpKV"
  def analyze(self, fileName, addr, fall, preds, succs, arch):
    print((addr, preds, succs))
    sys.stdout.flush()
    return []
