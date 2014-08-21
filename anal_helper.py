import os
import capnp
import holmes_capnp

def forkRegister(register, addr):
  pid = os.fork()
  if (pid == 0):
    client = capnp.TwoPartyClient(addr)
    holmes = client.ez_restore('holmes').cast_as(holmes_capnp.Holmes)
    register(holmes).wait()
  return pid
