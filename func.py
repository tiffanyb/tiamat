from holmes import *

class MarkFuncs():
  premises = [Premise("symbol", [Bind("fileName", "string")
                                ,Unbound("string")
                                ,Bind("addr", "addr")
                                ,Unbound("addr")
                                ,Unbound("addr")
                                ,Exact("func", "string")])]
  conclusions = [ConcTy("func", ["string", "addr"]),
                 ConcTy("reachable", ["string", "addr"])]
  name = "MarkFuncs"
  def analyze(self, fileName, addr):
    return [Conc("func", [fileName, addr]),
            Conc("reachable", [fileName, addr])]
