import json
from holmes import *

class Naive():
    # structured disassembly
    # Question: how to get the asm of exact file? Seems now it's getting all asms from every file
    premises = [Premise("arch", [Bind("fileName", "string"),
                                 Bind("arch", "string")])
               ,Premise("section", [Bind("fileName", "string"),
				     Unbound("string"),
				     Bind("addr_s", "addr"),
				     Unbound("addr"),
				     Bind("data", "blob"),
				     Exact(".text", "string")])
               ]
    conclusions = [ConcTy("func", ["string", "addr"])]

    name = "Naive"
    threshold = 0.5
    k = 10
    fileName = ""

    """
        Return k consecutive disassembly from addr_s within addr_e
    """
    def getConsecutiveAsms(self, asms, addr_s, addr_e, k):
        i = 0
        addr = addr_s
        res = []
        
        while i < k:
            try:
                asm, succ = asms[addr]
            except Exception:
                break
            if succ > e:
                break
            i += 1
            res.append(asm)
            addr = succ
        return res


    """
        Return a list of addresses associated with disassembly and the next instruction        address from address s to e
    """
    def getAsms(self, s, e):
        res = {}
        for addr in range(s, e + 1):
            # Question: should I query every time? Is there a better way to dump those disassemblies?
            asm = self.holmes.deriveFacts([Premise("hasasm", 
                                              [Exact(self.fileName, "string")
                                              ,Exact(addr, "addr")
                                              ,Bind("asm", "string")])
                                          ,Premise("fallthrough",
                                              [Exact(self.fileName, "string")
                                              ,Exact(addr, "addr")
                                              ,Bind("fall", "addr")])])
            print("==============")
            for i in asm:
                print(i)
            # print(asm[0])
            # asm = list(asm)
            print("----------")
            if len(asm) == 0:
                continue
            else:
                res[addr] = (str(asm[0]["asm"]), asm[0]["fall"])
        return res 


    """
        Match the disassembled & normalized (maybe) instructions with weighted prefix 
        tree, and return the score of such asms.
    """
    def match(self, asms):
        print(asms)
        return 0.6 


    def normalize(self, instr):
        return instr

 
    def analyze(self, fileName, arch, addr_s, data):
        addr_e = addr_s + len(data)
        asms = self.getAsms(addr_s, addr_e)
        addr = addr_s
        res = []
        self.fileName = fileName
        while addr <= addr_e:
            cons_asms = self.getConsecutiveAsms(asms, addr, addr_e, self.k)
            norm_cons_asms = map(lambda instr: self.normalize(instr), cons_asms)
            score = self.match(norm_cons_asms)
            # score = match(norm_cons_asms, trie)
            if score > threshold:
                res.append(addr)
        return map(lambda addr: Conc("func", [fileName, addr]) ,res)
        # print(data)
    	# print("=======================================")
    	# return [Conc("func", [fileName, 0xdeadbeaf])]


def check(holmes):
    funcs = holmes.deriveFacts([Premise("func", [Bind("fileName", "string")
                                            ,Bind("addr", "addr")])])
    for func in funcs:
        print("Function at " + hex(func['addr']))
