#!/usr/bin/env python
'''
A parser from Probabilistic Event-B models to Maude theories
See the grammar in EventB.g4
'''

from antlr4 import *
from EventBLexer import EventBLexer
from EventBListener import EventBListener
from EventBParser import EventBParser
import argparse
import sys
import textwrap
import traceback
from datetime import date

# Max number of steps in Maude (to stop the simulation in PVesTa)
MAXSTEP = 10000 

class BMaude(EventBListener):

    def __init__(self, output):
        '''output stream'''
        self._output = output
        #From ID to INT or List of values
        self._setdecl = {}
        #From ID to values
        self._ctedecl = {}
        #From ID to values
        self._vardecl = {}
        #Tests of reachability
        self._reachdecl = [] # List of strings with the expected values
        # Names of the evetns
        self._eventid = []  # List of strings
        self._anyvars = {}  # Any variables in events (initialized by each event)
        self._modvars = {}  # Modified variables in events (initialized in each event)
        self._ctxname = "" # Name of the context
        self._mchname = "" # Name of the machine
        self._lambda  = 0  # Counter for lambda expressions 
        self._lambdavar = {} # Lambda variables declared in an event
        self._mapfunc = set() # Set of map-like expressions
        self._defctes = set() # Defined constants 
        self._props   = {}    # Properties to be verified (from Nat to strings )



    #----------------------------
    # Some auxiliary definitions
    #----------------------------

    @staticmethod
    def prepstr(t, x):
        '''Adding quotes for types different to int and bool'''
        if t == str:
            return '"' + x + '"'
        elif t == bool:
            return "true" if x == "True"  else "false"
        elif t == int:
            return x


    def parseExpr(self, ctx:EventBParser.ExprContext):
        def binsymbol(sym:str, infix=True):
            '''Parsing left and right and adding the symbol'''
            if infix:
                return "("+ self.parseExpr(ctx.left) + ")" +  sym + "(" + self.parseExpr(ctx.right) + ")"
            else:
                return sym + "(" + self.parseExpr(ctx.left) + ", " + self.parseExpr(ctx.right) + ")"

        def unsymbol(sym:str, ctx):
            '''Parsing unary operators'''
            return sym + "(" + self.parseExpr(ctx) + ")"

        # Parentheses
        if type(ctx) == EventBParser.ParenthesesContext:
            v = self.parseExpr(ctx.inner) 
            return f' ( {v} )'
        # Basic values
        if type(ctx) == EventBParser.ExprValContext:
            return self.procType(ctx.val())

        # Arithmetic expressions
        if type(ctx) == EventBParser.ArithExprPMContext:
            return binsymbol( " + " if ctx.PLUS() else " - ")

        if type(ctx) == EventBParser.ArithExprTDContext:
            sym = ""
            if ctx.TIMES(): sym = " * "
            elif ctx.DIV(): sym = ' / '
            else: sym = " rem " 
            return binsymbol(sym)

        # Comparison 
        if type(ctx) == EventBParser.CompExprContext:
            return binsymbol( " =b " if ctx.EQ() else " <>b ")

        # Relational
        if type(ctx) == EventBParser.RelExprContext:
            sym = " " + ctx.RELSYM().getText() + " "
            return binsymbol(sym)

        # Sets
        if type(ctx) == EventBParser.SetExprContext:
            sym = ""
            if ctx.UNION(): return binsymbol("union", infix=False)
            if ctx.DIFFERENCE(): return binsymbol(" / ")
            if ctx.INTERSECTION(): return binsymbol("intersection", infix=False)
            if ctx.IN(): return binsymbol(" in ")
            if ctx.NOTIN(): return binsymbol(" nin ")

        # Boolean 
        if type(ctx) == EventBParser.BoolExprContext:
            if ctx.CONJ(): return binsymbol( " andb ")
            if ctx.DISJ(): return binsymbol( " orb ")
            if ctx.IMPL(): return binsymbol( " impb ")

        # Sets and relations
        if type(ctx) == EventBParser.DomRanCardExprContext:
            sym = ""
            if ctx.DOM(): sym = "dom"
            elif ctx.RAN(): sym = "ran"
            elif ctx.CARD(): sym = "card"
            
            return unsymbol(sym, ctx.expr())

        if type(ctx) == EventBParser.RelationExprContext:
            sym = ""
            if ctx.DOMRES():   sym = "dom-res"
            elif ctx.RANRES(): sym = "ran-res"
            elif ctx.OVERR():  sym = "overr"

            return binsymbol(sym, infix=False)

        if type(ctx) == EventBParser.FuncAppContext:
            return  '(' + self.parseExpr(ctx.expr()[0]) + " ) (" + self.parseExpr(ctx.expr()[1]) + ")"

        if type(ctx) == EventBParser.MapExprContext:
            _id = ctx.ID().getText()
            self._lambda += 1 # Naming the Map Expression
            lid = self._lambda
            self._lambdavar[_id] = None # No value since it is mapped to $$id
            eset = self.parseExpr(ctx.expr()[0])
            fexp = self.parseExpr(ctx.expr()[1])
            # Adding a map-like function and its equation
            #!! This translation works for EBSets and not for EBRel
            #!! It is also customized for arithmetic expressions
            fexp = fexp.replace(f'$${_id}', f'val(elt($$lbdn{lid}))')
            self._mapfunc.add(textwrap.dedent(
            f'''
  var $$lbd{lid}  : EBType .
  var $$lbdn{lid} : Nat . 
  var $$lbdS{lid} : EBSet . 
  op $$map{lid}   : EBType Configuration -> EBType .
  eq $$map{lid}(val( (empty).EBSet), C:Configuration) = val( (empty).EBSet) .
  eq $$map{lid}(val( (elt($$lbdn{lid}), $$lbdS{lid})), ({self.ruleWrapper('noevent')})) =
   union(({fexp}), $$map{lid}(val($$lbdS{lid}),{self.ruleWrapper('noevent')})) . 
            '''))
            return f''' $$map{lid}(({eset}), ({self.ruleWrapper('noevent')}))'''

        if type(ctx) == EventBParser.FilterExprContext:
            _id = ctx.ID().getText()
            self._lambda += 1 # Naming the Map Expression
            lid = self._lambda
            self._lambdavar[_id] = None # No value since it is mapped to $$id
            eset = self.parseExpr(ctx.expr()[0])
            fexp = self.parseExpr(ctx.expr()[1])
            # Adding a map-like function and its equation
            #!! This translation works for EBSets and not for EBRel
            #!! It is also customized for arithmetic expressions
            fexp = fexp.replace(f'$${_id}', f'val(elt($$lbdn{lid}))')
            self._mapfunc.add(textwrap.dedent(
            f'''
  var $$lbd{lid}  : EBType . 
  var $$lbdn{lid} : Nat . 
  var $$lbdS{lid} : EBSet . 
  op $$filter{lid}   : EBType Configuration -> EBType .
  eq $$filter{lid}(val( (empty).EBSet), C:Configuration) = val( (empty).EBSet) .
  eq $$filter{lid}(val( (elt($$lbdn{lid}), $$lbdS{lid})), ({self.ruleWrapper('noevent')})) =
     if ebset2bool({fexp}) 
     then union(val(elt($$lbdn{lid})), $$filter{lid}(val($$lbdS{lid}),{self.ruleWrapper('noevent')}))
     else $$filter{lid}(val($$lbdS{lid}),{self.ruleWrapper('noevent')})
     fi .
              '''))
            return f''' $$filter{lid}(({eset}), ({self.ruleWrapper('noevent')}))'''

            

    def procType(self,ctxV:EventBParser.ValContext, addVal=True):
        '''given a ctx returns tuples type,val. If addval is True, the value is
        wrapped with the val() constructor in Maude'''

        wrapperval = lambda x: "val(" + x + ")"
        wrapperid = lambda x: x 

        def procBType(val, addVal=True): # For basic types
            valT = val.getText()
            wrapper = wrapperval if addVal else wrapperid

            if val.INT():
                 return wrapper(f'elt({BMaude.prepstr(int, valT)})')
            elif val.boolV(): #valT == "True" or valT == "False" :
                return  wrapper(f'elt({BMaude.prepstr(bool, valT)})')
            else: # Strings/constants from a deferred set or name of constants/variables
                # A constant or a variable
                if valT in self._vardecl or valT in self._ctedecl or valT in self._lambdavar:
                    return f'$${valT}'
                # A parameter
                if valT in self._anyvars:
                    choice = self._anyvars[valT]
                    if type(choice) == tuple: # int-range
                        return f'choice({choice[0]}, {choice[1]})'
                    else: # List of values
                        return f'choice({choice})'

                if valT in self._defctes: # A constant
                    return  wrapper(f'elt({BMaude.prepstr(str, valT)})')

                print(f"[Warning] {valT} not defined")


        if type(ctxV)==EventBParser.BvalueContext: # Basic values
            return procBType(ctxV, addVal)

        if ctxV.bvalue(): # Basic types
            return procBType(ctxV.bvalue(), addVal)

        if ctxV.pvalue(): # tuples 
            wrapper = wrapperval if addVal else wrapperid
            if ctxV.pvalue().bvalue() : # basic values on the right and left hand sides
                bt1 = ctxV.pvalue().bvalue()[0]
                bt2 = ctxV.pvalue().bvalue()[1]

                bt1val = procBType( bt1, addVal=False)
                bt2val = procBType( bt2, addVal=False)

            else: # Expressions using { } as delimiter
                bt1val = self.parseExpr(ctxV.pvalue().expr()[0])
                bt2val = self.parseExpr(ctxV.pvalue().expr()[1])
            
            return wrapper(bt1val + " |-> " + bt2val)

        def ParseListValues(ctx):
            '''Parse a list of values from the production svaluelist'''
            if ctx.SEP(): # More elements in the list
                return self.procType(ctx.svalue(), addVal=False) + " , " + ParseListValues(ctx.svaluelist())

            return self.procType(ctx.svalue(), addVal=False)

        def ParseBLValue(ctx):
            '''Processing basic list of values'''
            if ctx.EMPTY(): # Empty set
                return 'val((empty).EBSet)'
            if ctx.EMPTYREL(): # Empty set of pairs
                return 'val((empty).EBRel)'

            if ctx.svaluelist(): # Explicit enumeration of values
                return f'val( ( {ParseListValues(ctx.svaluelist())} ) )'

            if ctx.INTRANGE(): #integer range of values
                bt1 = f'ebset2nat({self.parseExpr(ctx.expr()[0])})'
                bt2 = f'ebset2nat({self.parseExpr(ctx.expr()[1])})'

                return wrapperval(bt1 + " ..  " + bt2) 

        if ctxV.lvalue(): # List of values
            ctx = ctxV.lvalue()
            if ctx.CARTPROD(): # Cartesian products
                ctx1 = ctx.blvalue()[0]
                ctx2 = ctx.blvalue()[1]
                b1 = ParseBLValue(ctx1)
                b2 = ParseBLValue(ctx2)
                return f'make-rel({b1}, {b2})'

            else: # Simple lists
                ctx = ctx.blvalue()[0]
                return ParseBLValue(ctx)

    #-------------------------------------
    # Model related Definitions
    #-------------------------------------
    def enterModel(self, ctx:EventBParser.ModelContext):
        '''Beginning of the model'''
        s = textwrap.dedent(f'''
                --- Module generated by B2Maude ({date.today()})
                --- Context: {self._ctxname}
                --- Machine: {self._mchname}

                load ../../b2m-theory/ebmachine .
                ''')
        self._ctxname = ctx.context().ID().getText()
        self._mchname = ctx.machine().ID()[0].getText()
        self._output.write(s)


    ## ==========================
    ## Context related definitions
    ## ==========================

    def exitContext(self, ctx:EventBParser.ContextContext):
        ''' Generating Event-B's context information including
            the initialization of the sets and constants
        '''

        s = textwrap.dedent(f'''
                mod {ctx.ID()} is
                  inc EBMACHINE .

                  --- Context: Sets and constants
                  ''')

        # Initializing sets:
        # - single value to enumerate the elements
        # - or list of strings/ids
        def _strS(id):
            val = self._setdecl[id]
            if type(val) == int:
                self._defctes |= set((f'{id}{i}' for i in range(1, val+1)))
                return f"   ('{id} |-> gen-set(\"{id}\", {val}))"
            else:
                self._defctes |= set(str(x) for x in val)
                s = ' '.join('"'+x+'"' for x in val)
                return f"   ('{id} |-> gen-set(({s})))"
         
        s += "  eq init-sets = \n"
        if len(self._setdecl):
            s+= ',\n'.join(_strS(id) for id in self._setdecl )
        else:
            s+= "  empty "

        s+= "\n  .\n"

        # Initializing constants 
        def _strC(id):
            #!! Consider the other types here
            val = self._ctedecl[id]
            return f"   ('{id} |-> {val})" 

        s+= '\n  eq init-constants = \n'
        if len(self._ctedecl):
            s+= ',\n'.join(_strC(id) for id in self._ctedecl)
        else:
            s+= "  empty "

        s+= "\n  .\n" 

        self._output.write(s)

    def exitSetdef(self, ctx:EventBParser.SetdeclContext):
        '''Collecting info about set declarations'''
        setdecl = ctx.setdecl()
        idx = ctx.ID().getText()
        
        # INT -> Number of elements to be generated
        if setdecl.INT() is not None:
            self._setdecl[idx] = int(setdecl.INT().getText())
        else:
            '''A list of values'''
            self._setdecl[idx] = setdecl.listID().getText().split(',')

    def exitCtedef(self, ctx:EventBParser.CtedefContext):
        ''' Collecting info about constants '''
        _id = ctx.ID().getText()
        v = self.procType(ctx.val())
        self._ctedecl[_id] =  v

    ## =========================
    ## Machine related definitions
    ## =========================

    def exitVardecl(self, ctx:EventBParser.VardeclContext):
        '''Variable Declarations: Adding the IDs without values/types'''
        for x in ctx.ID():
            self._vardecl[x.getText()] = None


    @staticmethod
    def maudeVarName(_id):
        ''' Generating names for Maude variables'''
        return f'$${_id}'


    def exitInitst(self, ctx:EventBParser.InitstContext):
        ''' Initialization of the machine'''
        # !! Powerset case missing

        # Adding Maude's variables for Machine's variables and constants

        s = f'\n--- ===============================\n'
        s += f'\n--- VARIABLES \n'
        for _id in self._vardecl:
            v = self._vardecl[_id]
            # Variables before and after (')
            s+= " var " + BMaude.maudeVarName(_id) + " : EBType .\n"
        s += f'\n--- CONSTANTS \n'
        for _id in self._ctedecl:
            v = self._ctedecl[_id]
            s+= " var " + BMaude.maudeVarName(_id) + " : EBType .\n"

        # Variables for implementing the machine
        s+= textwrap.dedent( f''' 
         vars $$CNAME $$MNAME : Qid .
         vars $$SEv $$SEv' : SEvent .
         var  $$Sets : Map{{Qid, EBSet}} .
         var  $$Cte  : Map{{Qid, EBType}} .
         var  $$WEIGHT : Nat .
         var  $$GUARD :  Bool . 
        ''')
                
        s += f'\n--- ===============================\n'

        # Initializing variables 
        def _strV(id):
            #!! Consider the other types here
            val = self._vardecl[id]
            return f"   ('{id} |-> {val})" 

        for assgCtx in ctx.getChildren():
            v = self.procType(assgCtx.expr().val())
            _id = assgCtx.ID().getText()
            self._vardecl[_id] = v


        # Initialization for variables
        s += f'''\n  eq init-variables({self.contextWrapper()})\n   =\n '''
        if len(self._vardecl):
            s+= ',\n'.join(_strV(id) for id in self._vardecl)
        else:
            s+= "  empty "


        s+= f" .\n\n"
        self._output.write(s)



    def constantsCtx(self):
        '''Returning the context with the Maude variables
           handling the constants of the Context
        '''
        if self._ctedecl:
            return ' , '.join([ f"'{_id} |-> $${_id}" for _id in self._ctedecl])
        return "empty" 

    def variablesCtx(self):
        '''Returning the context with the Maude variables
           handling the variables of the machine
        '''
        return ' , '.join([ f"'{_id} |-> $${_id}" for _id in self._vardecl])

    def contextWrapper (self):
        '''
        Returning the Maude's variables used to define B-constants 
        '''
        return f'''  < $$CNAME : Context | sets : ($$Sets), constants : ({self.constantsCtx()}) > '''
                                    
    
    def ruleWrapper (self, events):
        '''
        Returning the usual context for equation and rules. (constants + variables)
        '''
        return textwrap.dedent(
        f''' {self.contextWrapper()}
       < $$MNAME : Machine | variables : ({self.variablesCtx()}), events : {events} > ''')

    def parseAnyVars(self,ctx):
        '''Returns a dictionary indexed by the id of the parameters and values that it can take
           In the case of int-range (n .. m), the value is a tuple with the two
           limits. In the case of range of strings, the value is the list of
           strings. 
        '''
        vany = {}
        if ctx.anydecl():
            for ctxvar in ctx.anydecl().anyvardef():
                _id = ctxvar.ID().getText()
                ctxrange = ctxvar.anyrange()

                if ctxrange.intrange():
                    li = self.parseExpr(ctxrange.intrange().expr()[0])
                    ls = self.parseExpr(ctxrange.intrange().expr()[1])
                    vany[_id] = li, ls
                elif ctxrange.strrange(): # List of values (strings)
                    values = ctxrange.strrange().listID().getText().split(',')
                    vany[_id] = ' '.join([ f'val(elt("{v}")) !' for v in  values  ])
                elif ctxrange.setrange(): # Expression resulting in a list of values
                    _exp = self.parseExpr(ctxrange.setrange().expr())
                    vany[_id] = _exp
        return vany

    def parametersEmpty(self):
        '''Returns a condition/guard (to be checked by Maude) telling if the
        set of values for a parameter is empty or not'''

        # For range of integer values
        lrange = [ f'ebset2nat({x[0]}) <= ebset2nat({x[1]})' for x in self._anyvars.values() if  type(x) == tuple ]

        # For list of values and set expressions
        lrange += [ f' is-empty( ({x}) ) == false ' for x in self._anyvars.values() if type(x) == str ]
        return lrange

    def parseProbList(self, ctx):
        '''Parsing elements of the form E1 @ p1 , ... , En @ pn'''

        def parseProbElem(ctxelem):
            return self.parseExpr(ctxelem.expr()) + " @ " + ctxelem.FLOAT().getText()

        exp = parseProbElem(ctx.probexpr())

        if ctx.problist(): # More elements in the choice
            return f' {exp}  {self.parseProbList(ctx.problist())}'
        else:
            return exp

    def parseThenAction(self, ctx):
        '''Parsing the assignments in the THEN section of the machine. Two kind
        of assignments are considered: x := expr and probabilistic choices'''
        modvar = {}
        for assg in ctx:
            if assg.simplassg(): # x:= expr
                assgctx = assg.simplassg()
                _id  = assgctx.ID().getText()
                _exp = self.parseExpr(assgctx.expr())
                modvar[_id] = _exp

            else: # x := { probchoice }
                assgctx = assg.probassg()
                _id  = assgctx.ID().getText()
                _exp = self.parseProbList(assgctx.problist())
                modvar[_id] = f'choice({_exp})'

        return modvar


    def newState(self, events):
        '''Returning the Maude's context with the new state of the variables'''

        # Variables not modified by the event
        unmodified =  [ f"'{_id} |-> $${_id}" for _id in self._vardecl if _id not in self._modvars]

        # Modified variables
        modified = [ f"'{_id} |-> {_expr}" for _id,_expr in self._modvars.items() ]

        return f'< $$MNAME : Machine | variables : ({" , ".join(unmodified + modified)}) , events : {events} > '''


    # Enter a parse tree produced by EventBParser#eventdecl.
    def enterEventdecl(self, ctx:EventBParser.EventdeclContext):
        self._lambdavar = {}

    def exitEventdecl(self, ctx:EventBParser.EventdeclContext):
        ''' Declaration of Maude's conditional rule defining the event'''
        #Fix me: The Any statements are not completely handled

        evtid = ctx.ID().getText()
        self._eventid.append("'" + evtid)

        s = textwrap.dedent(
        f'''
        ----------------------------
        --- Event {evtid}
        ----------------------------
        ''')

        # Equation determining if the event is enabled
        vw = self.parseExpr(ctx.expr()) # Value of the weight
        vw = f'ebset2nat({vw})'
        vg = self.parseExpr(ctx.wheredecl().expr())
        vg = f'ebset2bool({vg})'

        # Handling parameter declarations
        self._anyvars = self.parseAnyVars(ctx)
        anycond = " and ".join(self.parametersEmpty())
        if anycond:
            anycond = " and " + anycond

        # Action of the event
        self._modvars = self.parseThenAction(ctx.evassg()) # Mapping from the IDs of the modified variables and the RHS expression

        s += textwrap.dedent(
        f''' 
  --- Activation of the Event {evtid}
  ceq [{evtid}] :
      {self.ruleWrapper('( ( $$SEv, ev(\'' + f'{evtid}, unknown) ) )')}
      =
      if $$WEIGHT > 0 and $$GUARD == true
      then 
        {self.ruleWrapper('(($$SEv, ev(\'' + f'{evtid}, enable($$WEIGHT))))')}
      else
        {self.ruleWrapper('(($$SEv, ev(\'' + f'{evtid}, blocked)))')}
      fi
  if      $$WEIGHT := {vw} 
       /\\ $$GUARD  := {vg} {anycond}
  .
  
  --- Change of state for event {evtid}
  rl [{evtid}] : 
      {self.ruleWrapper('ev(\'' + f'{evtid}, execute)')}
      =>
      {self.contextWrapper()}
      {self.newState('ev(\'' + f'{evtid}, running)')}
      . ''')

        self._output.write(s)


    def exitModel(self, ctx:EventBParser.MachineContext):
        ''' End of the machine definition'''
        s = ""
    
        # Adding auxiliary map-like functions
        if self._mapfunc : 
            s+= textwrap.dedent(
            f'''--- Auxiliary map-like functions
            {" ".join(self._mapfunc)}
--- ---------------------------
            ''')


        # Adding the initialization of the state of the events
        levent = ','.join([ f'ev({id}, unknown)' for id in self._eventid])

        # Properties
        sprop = ""
        for n,v in self._props.items():
            sprop +=  textwrap.dedent(f'''
              eq prop({n}, {self.contextWrapper()} < $$MNAME : Machine | variables : ({self.variablesCtx()}), events : $$SEv > ) 
                = toFloat(({v})) .
                ''')
            

        s+= textwrap.dedent(f'''
  --- Initialization of events
  eq init-events = {levent} .
  
  
  --- ------------
  --- Properties  
  --- ------------
  var SYS : Configuration .
  
  
  --- This definition depends on the system
  --- Change 1.0 with, for instance,   float(ebset2nat($$n)) 
  --- eq val(1, Conf < $$MNAME : Machine | variables: ({self.variablesCtx()}), events : $$SEv > ) = 1.0 . 
  --- Properties can be also defined in the .b file with a section PROPERTIES
  
  {sprop}

  ---- Defining the initial state
  op initState : -> Configuration .
  eq initState = init-machine('{self._ctxname}, '{self._mchname}) .
endm

eof

--- example of use

--- One step of rewriting
rew [1] initState . 

--- Search for all reachable states satisfying prop(1)
search initState =>* SYS such that SYS |= prop(1) .

--- Model Checking 
red modelCheck(initState, True) .

--- Umaudemc for stochastic model checking
umaudemc scheck file.maude initState formula.quatex

''')

        # Adding tests for reachability
        if self._reachdecl:
            s+= ''' search [1] init-machine =>* 
                < state : machine | variables : ( VMap:Map{Qid, EBSet}, 
                '''
            #', \n'.join()

            s+= ',  \n'.join(self._reachdecl)
            s+= '''
            )
            , REST:AttributeSet > .


            '''
        self._output.write(s)

    
    # -------------------------------------
    # Encoding of properties to be verified
    # -------------------------------------
    def enterProps(self, ctx:EventBParser.PropsContext):
        '''List in the section PROPERTIES at the end of the machine'''

        def parseProperty(ctx):
            n = len(self._props) + 1
            self._props[n] = self.parseExpr(ctx.prop().expr())

            if ctx.proplist():
                parseProperty(ctx.proplist())

        parseProperty(ctx.proplist())

def main(fin, fout):
    try:
        ipt = FileStream(fin)
        lexer = EventBLexer(ipt)
        stream = CommonTokenStream(lexer)
        parser = EventBParser(stream)
        tree = parser.model()
        output = open(fout,'w')
        printer = BMaude(output)
        walker = ParseTreeWalker()
        walker.walk(printer, tree)
        output.close()
        print(f'output: {fout}')
    except Exception as E:
        print(f'Error processing {fin}.\n {E}')
        traceback.print_exc()

if __name__ == '__main__':

   parser=argparse.ArgumentParser( 
            description=''' From Event-B to Maude specifications ''' , 
                        formatter_class=argparse.RawTextHelpFormatter )

   parser.add_argument('--output', type=str, default="./out.maude", 
                       help='Maude output file')

   parser.add_argument('--input',  type=str,
                        required = True,
                       help='Event-B file')
   args=parser.parse_args()
   main(args.input, args.output)

