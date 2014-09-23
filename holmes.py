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
  elif val.which == 'listVal':
    return list(map(fromDyn, val.listVal))
  else:
    raise TypeError("Unknown type input")

class Blob: pass

def toDyn(tgt, val):
  if isinstance(val, str):
    tgt.stringVal = val
  elif isinstance(val, int):
    tgt.addrVal = val
  elif isinstance(val, bytes):
    tgt.blobVal = val
  elif isinstance(val, dict):
    tgt.jsonVal = json.dumps(val)
  elif isinstance(val, list):
    tgt.jsonVal = json.dumps(val)
  else:
    raise TypeError("Unknown type output: " + str(type(val)))

def toDynS(val):
  if isinstance(val, str):
    return {'stringVal' : val}
  elif isinstance(val, int):
    return {'addrVal' : val}
  elif isinstance(val, bytes):
    return {'blobVal' : val}
  elif isinstance(val, dict):
    tgt.jsonVal = json.dumps(val)
  elif isinstance(val, list):
    tgt.jsonVal = json.dumps(val)
  else:
    raise TypeError("Unknown type output: " + str(type(val)))


def loadCtx(context):
  res = {}
  for var,val in context.items():
    res[var] = fromDyn(val)
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

class Forall:
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

def convertTemplates(templates, target):
  argNames = []
  premLen = len(templates)
  premiseBuilder = target
  for i in range(0, premLen):
    premise = templates[i]
    premiseBuilder[i].factName = premise.name
    args = premise.args
    argLen = len(args)
    argBuilder = premiseBuilder[i].init('args', argLen)
    for j in range(0, argLen):
      if isinstance(args[j], Bind):
        var = args[j].var
        if var not in argNames:
          argNames.append(var)
        argBuilder[j].bound = argNames.index(var)
      elif isinstance(args[j], Forall):
        var = args[j].var
        argNames.append(var)
        argBuilder[j].forall = argNames.index(var)
      elif isinstance(args[j], Exact):
        toDyn(argBuilder[j].exactVal, args[j].val)
      elif isinstance(args[j], Unbound):
        argBuilder[j].unbound = None
      else:
        argBuilder[j].unbound = None
  return argNames
 

def register(analysis, addr):
  client = capnp.TwoPartyClient(addr)
  holmes = client.ez_restore('holmes').cast_as(holmes_capnp.Holmes)
  analysis.holmes = Holmes(addr)
  for premise in analysis.premises:
    argTyper = []
    for arg in premise.args:
      argTyper += [{arg.typ : None}]
    if not holmes.registerType(factName = premise.name, argTypes = argTyper).wait():
      raise TypeError("Type mismatch for premise: " + str(premise))
  for conc in analysis.conclusions:
    argTyper = []
    for ty in conc.argtys:
      argTyper += [{ty : None}]
    if not holmes.registerType(factName = conc.name, argTypes = argTyper).wait():
      raise TypeError("Type mismatch for conclusion: " + str(conc))
  req = holmes.analyzer_request()
  req.name = analysis.name
  premLen = len(analysis.premises)
  premiseBuilder = req.init('premises', premLen)
  argNames = convertTemplates(analysis.premises, premiseBuilder)
  class Analysis(holmes_capnp.Holmes.Analysis.Server):
    def analyze (self, context, _context, **kwargs):
      cdict = dict(zip(argNames, context))
      ctx = loadCtx(cdict)
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

class Fact:
  def __init__(self, name, args):
    self.name = name
    self.args = args
  def getRaw(self):
    return {'factName' : self.name,
            'args'     : list(map(toDynS, self.args))}

class Holmes:
  def __init__(self, addr):
    self.client = capnp.TwoPartyClient(addr)
    self.holmes = self.client.ez_restore('holmes').cast_as(holmes_capnp.Holmes)
  def setFacts(self, facts):
    self.holmes.set(list(map(lambda f: f.getRaw(), facts))).wait()
  def deriveFacts(self, templates):
    req = self.holmes.derive_request()
    targetBuilder = req.init('target', len(templates))
    argNames = convertTemplates(templates, targetBuilder)
    resp = req.send().wait()
    for ctx in resp.ctx:
      cdict = dict(zip(argNames, ctx))
      yield loadCtx(cdict)
