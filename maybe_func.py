import capnp
import holmes_capnp

class MaybeFunc(holmes_capnp.Holmes.Analysis.Server):
  def analyze(self, premises, _context, **kwargs):
    res = []
    for premise in premises:
      der = {'factName' : "func",
             'args'     : [{'stringVal' : premise.args[0].stringVal},
                           {'addrVal'   : premise.args[2].addrVal}]}
      der2 = {'factName' : "reachable",
              'args'     : [{'stringVal' : premise.args[0].stringVal},
                            {'addrVal'   : premise.args[2].addrVal}]}
      res += [der, der2]
    _context.results.init('derived', len(res))
    _context.results.derived = res

def register(holmes):
  holmes.registerType(factName = 'func', argTypes = ['string', 'addr']).wait()
  holmes.registerType(factName = 'reachable', argTypes = ['string', 'addr']).wait()
  
  req = holmes.analyzer_request()
  req.name = "markFuncs"
  req.analysis = MaybeFunc()
  premiseBuilder = req.init('premises', 1)
  premiseBuilder[0].factName = "symbol"
  args = premiseBuilder[0].init('args', 6)
  args[0].unbound = None
  args[1].unbound = None
  args[2].unbound = None
  args[3].unbound = None
  args[4].unbound = None
  args[5].exactVal = {'stringVal' : "func"}
  return req.send()
