# EventB2Maude

EventB2Maude maps [Event-B](http://www.event-b.org/) and probabilistic
Event-B models to  rewrite theories executable in
[Maude](http://maude.cs.illinois.edu/w/index.php/The_Maude_System). This
repository contains the base rewrite theory needed to define sorts and
operations to represent declared types/sets and constants of any Event-B
context, as well as the infrastructure needed to encode the variables and the
events of any probabilistic Event-B machine. 

A parser written in [Python 3.12](https://www.python.org/downloads/release/python-3120/) and
[Antlr4](https://pypi.org/project/antlr4-python3-runtime/) allows for extending
the base theory to fully encode (probabilistic) Event-B models in Maude.  The
resulting rewrite theory can be used for:

 1. Simulation by rewriting,
 2. Seachability analysis, 
 3. LTL model checking, and  
 4. Stochastic model checking

## Getting started

The translation of Event-B models into Maude theories require Python 3.12 and
Antlr4. Simulation by rewriting, reachability analysis and LTL model checking
requires [Maude 3.5](https://maude.cs.illinois.edu/wiki/Maude_download_and_installation).
Stochastic model checking requires
[umaudemc](https://github.com/fadoss/umaudemc).

## Case studies

The directory [examples](./examples) contains several case studies and
simulation results, including:

1. Models in Chapters 2 (*Controlling cars on a bridge*), 3 (*A mechanical
   press controller*), 4 (*A simple file transfer protocol*), 6 (*Bounded
   re-transmission protocol*) and 7 (*Development of a concurrent program*) in
   the [Event-B book](https://www.cambridge.org/core/books/modeling-in-eventb/F39FF5F1B60F0AA585718B8E6A4F9DD7). 
2. Different variants of a bounded retransmission protocol. 
3.  A model of a network of agents that agree (positive weight) and disagree
    (negative weight) on a given subject and finding the probability of
    reaching a consensus. 
4. Some mechanical systems including a  controller for a landing gear system
   and an emergency brake system.
5. A P2P protocol.

See the references in [examples](./examples) for further details. 

## Structure of the project
- The directory `b2m-theory` contains the base rewrite theory for representing
  any (probabilistic) Event-B context and machine. The module `EB-TYPE` defines
  most of the operations allowed in Event-B specifications.
- In `parser`, there is the Antlr grammar used as well the Python script
  `B2Maude` that implements the parser. 
- Some examples of Event-B specifications are in the directory `examples`.
- The directory `scripts` includes some bash scripts needed to automate the
  execution of simulations with umaudemc. 
