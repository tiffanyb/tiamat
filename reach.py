from holmes import *

class ReachSucc:
  premises = [Premise("reachable", [Bind("fileName", "string")
                                   ,Bind("addr", "addr")])
             ,Premise("succ", [Bind("fileName", "string")
                              ,Bind("addr", "addr")
                              ,Bind("succ", "addr")])]
  conclusions = [ConcTy("reachable", ["string", "addr"])]
  name = "Reach Successors"
  def analyze(self, fileName, addr, succ):
    return [Conc("reachable", [fileName, succ])]
