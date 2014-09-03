import capnp
import holmes_capnp
import json
from subprocess import (Popen, PIPE)

toil = "/home/maurer/Sources/bap-lifter/toil.native"

def loadVal(val):
  if val.which == 'stringVal':
    return val.stringVal
  elif val.which == 'addrVal':
    return val.addrVal
  elif val.which == 'blobVal':
    return val.blobVal

def loadCtx(context):
  res = {}
  for binding in context:
    res[binding.var] = loadVal(binding.val)
  return res

class ToIL(holmes_capnp.Holmes.Analysis.Server):
  def analyze(self, context, premises, _context, **kwargs):
    ctx = loadCtx(context)
    toilProc = Popen([toil, '--arch', ctx['arch'], '--addr', str(ctx['addr']),'--format' , 'json'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    toilProc.stdin.write(ctx['data'])
    toilProc.stdin.close()
    jstr = toilProc.stdout.read().decode()
    try:
      out = json.loads(jstr)
      _context.results.init('derived', 1)
      _context.results.derived = [{'factName' : 'hasil',
                                   'args'     : [{'stringVal' : ctx['fileName']},
                                                 {'addrVal'   : ctx['addr']},
                                                 {'stringVal' : jstr}]}]
    except ValueError:
      print("No IL")
      print(ctx)
      print(jstr)
    #_context.results.init('derived', len(res))
    #_context.results.derived = res

def register(holmes):
  holmes.registerType(factName = 'hasil', argTypes = ['string', 'addr', 'string']).wait()
  holmes.registerType(factName = 'arch', argTypes = ['string', 'string']).wait()
  holmes.registerType(factName = 'reachable', argTypes = ['string', 'addr']).wait()
  holmes.registerType(factName = 'word128', argTypes = ['string', 'addr', 'blob']);

  req = holmes.analyzer_request()
  req.name = 'toil'
  req.analysis = ToIL()
  premiseBuilder = req.init('premises', 3)
  premiseBuilder[0].factName = "arch"
  archArgs = premiseBuilder[0].init('args', 2)
  archArgs[0].bound   = "fileName"
  archArgs[1].bound = "arch"
  premiseBuilder[1].factName = "reachable"
  reachArgs = premiseBuilder[1].init('args', 2)
  reachArgs[0].bound = "fileName"
  reachArgs[1].bound = "addr"
  premiseBuilder[2].factName = "word128"
  dataArgs = premiseBuilder[2].init('args', 3)
  dataArgs[0].bound = "fileName"
  dataArgs[1].bound = "addr"
  dataArgs[2].bound = "data"
  return req.send()
