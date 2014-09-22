#!/usr/bin/env python3
from subprocess import (Popen, PIPE)
import subprocess
import capnp
import os
import sys
dbname = 'holmes_test'

container = "obj.holmes"
chunker = "chunk.holmes"

subprocess.check_call('echo "drop database ' + dbname + '; create database ' + dbname + ';" | psql', shell=True)

env = os.environ.copy()
env['PGDATABASE'] = dbname
holmesProc = Popen(['holmes'], stdout=PIPE, env=env)

port = int(holmesProc.stdout.readline())
os.dup2(sys.stdout.fileno(), holmesProc.stdout.fileno())

addr = "localhost:" + str(port)

analProgs = [container, chunker]
analProcs = []
for prog in analProgs:
  analProcs.append(Popen([prog, addr]))

import func
import toil
import succ
import reach
import dumpKV
from holmes import *
pymods = [func.MarkFuncs(), toil.ToIL(), succ.LooseSucc(), reach.ReachSucc()]
pypids = []
for pymod in pymods:
  pypids += [forkRegister(pymod, addr)]

print("Port: " + str(port))

fileName = sys.argv[1]
with open(fileName, mode='rb') as file:
    fileContent = file.read()

holmes = Holmes(addr)

#Races
import time
import datetime
time.sleep(1);

begin = datetime.datetime.now()
holmes.setFacts([Fact("file", [fileName, fileContent])])
done = datetime.datetime.now()

print(done - begin)

funcs = holmes.deriveFacts([Premise("func", [Bind("fileName", "string")
                                            ,Bind("addr", "addr")])
                          ,Premise("reaches", [Bind("fileName", "string")
                                              ,Bind("addr", "addr")
                                              ,Forall("body", "addr")])])
for func in funcs:
  print("Function at: " + hex(func['addr']))
  for addr in func['body']:
    il = holmes.deriveFacts([Premise("hasil", [Exact(func['fileName'], "string")
                                              ,Exact(addr, "addr")
                                              ,Bind("il", "json")])])
    print(hex(addr) + ":")
    il = list(il)
    if len(il) == 0:
      print("No IL available")
    else:
      print(str(il[0]['il']))

    asm = holmes.deriveFacts([Premise("hasasm", [Exact(func['fileName'], "string")
                                                ,Exact(addr, "addr")
                                                ,Bind("asm", "string")])])
    asm = list(asm)
    if len(asm) == 0:
      print("No Disassembly available")
    else:
      print(str(asm[0]['asm']))

import signal
for pypid in pypids:
  os.kill(pypid, signal.SIGKILL)
for analProc in analProcs:
  analProc.terminate()
holmesProc.terminate()
os.unlink('/tmp/bapd')
