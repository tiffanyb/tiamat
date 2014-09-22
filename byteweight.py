import json
from holmes import *

"""
class ByteWeight():
    # structured disassembly
    premises = [Premise("arch", [Bind("fileName", "string")])]

    # Question:
    # 1. can "func" return a list of func? Or a list is not what you want?
    # 2. is "reachable" neccessary?
    conclusions = [ConcTy("func", ["string", "addr"]),
    	           ConcTy("reachable", ["string", "addr"])]

    name = "ByteWeight"
"""

class Naive():
    # structured disassembly
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

    def analyze(self, fileName, arch, addr_s, data):
    	# print(data)
    	# print("=======================================")
    	return [Conc("func", [fileName, 0xdeadbeaf])]

def check(holmes):
    funcs = holmes.deriveFacts([Premise("func", [Bind("fileName", "string")
                                            ,Bind("addr", "addr")])])
    for func in funcs:
        print("Function at " + hex(func['addr']))
