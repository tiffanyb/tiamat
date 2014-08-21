#!/bin/env python
from subprocess import (Popen, PIPE)
import capnp
import holmes_capnp

holmes = "/home/maurer/Sources/holmes-build/server/holmes"
container = "/home/maurer/Sources/container-build/obj.holmes"
chunker = "/home/maurer/Sources/container-build/chunk.holmes"

holmesProc = Popen([holmes], stdout=PIPE, stderr=PIPE)

port = int(holmesProc.stdout.readline())

addr = "localhost:" + str(port)

analProgs = [container, chunker]
analProcs = []
for prog in analProgs:
  analProcs.append(Popen([prog, addr]))

import maybe_func
import toil
from anal_helper import forkRegister
pymods = [maybe_func, toil]
pypids = []
for pymod in pymods:
  pypids += [forkRegister(pymod.register, addr)]

print("Port: " + str(port))

fileName = "/home/maurer/base64.arm"
with open(fileName, mode='rb') as file:
    fileContent = file.read()

client = capnp.TwoPartyClient(addr)
holmes = client.ez_restore('holmes').cast_as(holmes_capnp.Holmes)
holmes.set({'factName' : "file",
            'args'     : [{'stringVal' : fileName},
                          {'blobVal'   : fileContent}]}).wait()

import os
import signal
for pypid in pypids:
  os.kill(pypid, signal.SIGKILL)
for analProc in analProcs:
  analProc.terminate()
holmesProc.terminate()
