#!/bin/env python
from subprocess import (Popen, PIPE)
import subprocess
import capnp
import holmes_capnp
import os
import sys
if len(sys.argv) <= 1:
  holmes = "/home/maurer/Sources/holmes-build/server/holmes"
  holmesCall = [holmes]
elif sys.argv[1] == 'valgrind':
  holmes = "/home/maurer/Sources/holmes-build/server/holmes"
  holmesCall = ['valgrind', '--leak-check=full', holmes]
elif sys.argv[1] == 'asan':
  holmes = "/home/maurer/Sources/holmes-asan/server/holmes"
  holmesCall = [holmes]

dbname = 'holmes_test'

container = "/home/maurer/Sources/container-build/obj.holmes"
chunker = "/home/maurer/Sources/container-build/chunk.holmes"

subprocess.check_call('echo "drop database ' + dbname + '; create database ' + dbname + ';" | psql', shell=True)

env = os.environ.copy()
env['PGDATABASE'] = dbname
env['GLOG_logtostderr'] = '1'
env['GLOG_stderrthreshold'] = '0'
holmesProc = Popen(holmesCall, stdout=PIPE, env=env)

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
from holmes import forkRegister
pymods = [func.MarkFuncs(), toil.ToIL(), succ.LooseSucc(), reach.ReachSucc(), dumpKV.DumpKV()]
pypids = []
for pymod in pymods:
  pypids += [forkRegister(pymod, addr)]

print("Port: " + str(port))

fileName = "/home/maurer/hello"
with open(fileName, mode='rb') as file:
    fileContent = file.read()

client = capnp.TwoPartyClient(addr)
holmes = client.ez_restore('holmes').cast_as(holmes_capnp.Holmes)

#Races
import time
import datetime
time.sleep(1);

begin = datetime.datetime.now()
holmes.set([{'factName' : "file",
             'args'     : [{'stringVal' : fileName},
                           {'blobVal'   : fileContent}]}]).wait()
done = datetime.datetime.now()

print(done - begin)

import signal
for pypid in pypids:
  os.kill(pypid, signal.SIGKILL)
for analProc in analProcs:
  analProc.terminate()
holmesProc.terminate()
