from holmes import *

class ReachSucc:
  premises = [Premise("reaches", [Bind("fileName", "string")
                                 ,Bind("base", "addr")
                                 ,Bind("addr", "addr")])
             ,Premise("succ", [Bind("fileName", "string")
                              ,Bind("addr", "addr")
                              ,Bind("succ", "addr")])]
  conclusions = [ConcTy("reachable", ["string", "addr"]),
                 ConcTy("reaches", ["string", "addr", "addr"])]
  name = "Reach Successors"
  def analyze(self, fileName, base, addr, succ):
    return [Conc("reachable", [fileName, succ]),
            Conc("reaches", [fileName, base, succ])]
