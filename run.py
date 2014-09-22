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
env['GLOG_logtostderr'] = '1'
env['GLOG_stderrthreshold'] = '0'
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

import signal
for pypid in pypids:
  os.kill(pypid, signal.SIGKILL)
for analProc in analProcs:
  analProc.terminate()
holmesProc.terminate()
os.unlink('/tmp/bapd')
