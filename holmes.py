import capnp
import os
import holmes_capnp
import json

def fromDyn(val):
  if val.which == 'stringVal':
    return val.stringVal
  elif val.which == 'addrVal':
    return val.addrVal
  elif val.which == 'blobVal':
    return val.blobVal
  elif val.which == 'jsonVal':
    return json.loads(val.jsonVal)
  else:
    raise TypeError("Unknown type input")

class Blob: pass

def toDyn(tgt, val):
  if isinstance(val, str):
    tgt.stringVal = val
  elif isinstance(val, int):
    tgt.addrVal = val
  elif isinstance(val, Blob):
    pass # No blob support for returns yet
  elif isinstance(val, dict):
    tgt.jsonVal = json.dumps(val)
  elif isinstance(val, list):
    tgt.jsonVal = json.dumps(val)
  else:
    raise TypeError("Unknown type output: " + str(type(val)))

def loadCtx(context):
  res = {}
  for binding in context:
    res[binding.var] = fromDyn(binding.val)
  return res

class Premise:
  def __init__(self, name, args):
    self.name = name
    self.args = args

class ConcTy:
  def __init__(self, name, argtys):
    self.name = name
    self.argtys = argtys

class Conc:
  def __init__(self, name, args):
    self.name = name
    self.args = args

class Bind:
  def __init__(self, var, typ):
    self.var = var
    self.typ = typ

class Unbound:
  def __init__(self, typ):
    self.typ = typ

class Exact:
  def __init__(self, val, typ):
    self.val = val
    self.typ = typ

def register(analysis, addr):
  client = capnp.TwoPartyClient(addr)
  holmes = client.ez_restore('holmes').cast_as(holmes_capnp.Holmes)
  for premise in analysis.premises:
    argTyper = []
    for arg in premise.args:
      argTyper += [arg.typ]
    if not holmes.registerType(factName = premise.name, argTypes = argTyper).wait():
      raise TypeError("Type mismatch for premise: " + str(premise))
  for conc in analysis.conclusions:
    if not holmes.registerType(factName = conc.name, argTypes = conc.argtys).wait():
      raise TypeError("Type mismatch for conclusion: " + str(conc))
  req = holmes.analyzer_request()
  req.name = analysis.name
  premLen = len(analysis.premises)
  premiseBuilder = req.init('premises', premLen)
  for i in range(0, premLen):
    premise = analysis.premises[i]
    premiseBuilder[i].factName = premise.name
    args = premise.args
    argLen = len(args)
    argBuilder = premiseBuilder[i].init('args', argLen)
    for j in range(0, argLen):
      if isinstance(args[j], Bind):
        argBuilder[j].bound = args[j].var
      elif isinstance(args[j], Exact):
        toDyn(argBuilder[j].exactVal, args[j].val)
      elif isinstance(args[j], Unbound):
        argBuilder[j].unbound = None
      else:
        argBuilder[j].unbound = None
  class Analysis(holmes_capnp.Holmes.Analysis.Server):
    def analyze (self, context, premises, _context, **kwargs):
      ctx = loadCtx(context)
      out = analysis.analyze(**ctx)
      _context.results.init('derived', len(out))
      for i in range(0, len(out)):
        concl = out[i]
        _context.results.derived[i].factName = concl.name
        _context.results.derived[i].init('args', len(concl.args))
        for j in range(0, len(concl.args)):
          toDyn(_context.results.derived[i].args[j], concl.args[j])
  req.analysis = Analysis()
  req.send().wait()

def forkRegister(obj, addr):
  pid = os.fork()
  if pid == 0:
    register(obj, addr)
    sys.exit(0)
  return pid
