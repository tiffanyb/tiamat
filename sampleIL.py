from holmes import *
class SampleIL:
  def analyze(self, fileName, addr, il):
    print("fileName: " + fileName)
    print("addr: " + str(addr))
    print("first il op type: " + str(il[0].keys()))
    return []
  premises = [Premise('hasil', [Bind("fileName", "string")
                                ,Bind("addr", "addr")
                                ,Bind("il", "json")])]
  conclusions = []
  name = "SampleIL"
