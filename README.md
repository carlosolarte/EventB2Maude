# EventB2Maude

EventB2Maude maps probabilistic [Event-B](http://www.event-b.org/) models [1]
to probabilistic rewrite theories [2]. This repository contains the base
rewrite theory written in
[Maude](http://maude.cs.illinois.edu/w/index.php/The_Maude_System) needed to
define sorts and operations to represent declared types/sets and constants of
any Event-B context, as well as the infrastructure needed to encode the
variables and the events of any probabilistic Event-B machine. Moreover, a
parser written in [Python
3.10](https://www.python.org/downloads/release/python-3100/) and
[Antlr4](https://pypi.org/project/antlr4-python3-runtime/) allows for extending
the base theory to fully encode (probabilistic) Event-B models in Maude.  The
resulting theory can be used for simulation in PMaude [2] and is amenable to
statistical model checking in PVeStA [3] or MultiVeStA [4]. 

## Getting started

For using [PVeSta](http://maude.cs.uiuc.edu/tools/pvesta/), or
[MultiVeStA](https://sysma.imtlucca.it/tools/tool_multivesta/) Maude alpha110
and Java 1.8 are needed. Moreover, for using the parser, Python 3.10 and Antlr4
are needed. 

## Case studies

The directory [examples](./examples) contains several case studies and
simulation results, including:
- A controller for a landing gear system.
- An emergency brake system.
- A P2P protocol.
- Different variants of a bounded retransmission protocol. 
- Models in Chapters 2 (*Controlling cars on a bridge*), 3 (*A mechanical
  press controller*), 4 (*A simple file transfer protocol*), 6 (*Bounded
  re-transmission protocol*) and 7 (*Development of a concurrent program*) in
  the Event-B book [5]. 
- A model of a network of agents that agree (positive weight) and disagree
  (negative weight) on a given subject and finding the probability of reaching
  a consensus. 

See the references in [examples](./examples) for further details. 

## Structure of the project
- The directory `m-theory` contains the base rewrite theory for representing
  any (probabilistic) Event-B context and machine. The module `EB-TYPE` defines
  most of the operations allowed in Event-B specifications [5].
- In `parser`, there is the Antlr grammar used as well the Python script
  `B2Maude` that implements the parser. 
- Some examples of Event-B specifications are in the directory `examples`.
- The directory `scripts` includes some bash scripts needed to automate the
  execution of simulations with PVeSta and MultiVeStA.

## References
[1] Mohamed Amine Aouadhi, Benoît Delahaye, Arnaud Lanoix: Introducing
probabilistic reasoning within Event-B. Softw. Syst. Model. 18(3): 1953-1984
(2019)

[2] Gul A. Agha, José Meseguer, Koushik Sen: PMaude: Rewrite-based
Specification Language for Probabilistic Object Systems. Electron. Notes Theor.
Comput. Sci. 153(2): 213-239 (2006)

[3] Musab AlTurki, José Meseguer: PVeStA: A Parallel Statistical Model Checking
and Quantitative Analysis Tool. CALCO 2011: 386-392

[4] Stefano Sebastio, Andrea Vandin: MultiVeStA: statistical model checking for
discrete event simulators. VALUETOOLS 2013: 310-315

[5] Jean-Raymond Abrial: Modeling in Event-B - System and Software Engineering.
Cambridge University Press (2010) 
