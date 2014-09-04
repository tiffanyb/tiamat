from holmes import *
import base64
class LooseSucc():
  premises = [Premise("hasil", [Bind("fileName", "string")
                               ,Bind("addr", "addr")
                               ,Bind("il", "json")])
             ,Premise("fallthrough", [Bind("fileName", "string")
                                     ,Bind("addr", "addr")
                                     ,Bind("fall", "addr")])]
  conclusions = [ConcTy("succ", ["string", "addr", "addr"])]
  name = "Loose Successor"
  def getTargets(self, il):
    tgts = []
    uncond = False
    for stmt in il:
      if "jmp" in stmt:
        uncond = True
        texp = stmt["jmp"]["target"]
        if "inte" in texp:
          val = texp["inte"]["int"]
          valb = int.from_bytes(base64.b64decode(val), byteorder='little')
          tgts += [valb]
      if "while-stmt" in stmt:
        tgts += getTargets(stmt["while-stmt"]["loop-body"])[0]
      if "if-stmt" in stmt:
        tt,tj = getTargets(stmt["if-stmt"]["true-branch"])
        ft,fj = getTargets(stmt["if-stmt"]["true-branch"])
        uncond |= (tj & fj)
        tgts += tt
        tgts += ft
    return (tgts, uncond)
  def analyze(self, fileName, addr, il, fall):
    tgts, uncond = self.getTargets(il)
    if not uncond:
      tgts += [fall]
    concs = []
    for tgt in tgts:
      concs += [Conc("succ", [fileName, addr, tgt])]
    return concs
