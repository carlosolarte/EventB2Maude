# First refinement car-bridge system #
# Chapter 1: Abrial's book #
#
CONTEXT ctxCarBridge
SETS 
CONSTANTS 
    d : Nat := 10
END

MACHINE CarBridgeSystem
  SEES ctxCarBridge

  VARIABLES

    a b c 

  INVARIANTS

    a : Nat 
    b : Nat
    c : Nat 

  INITIALISATION

    a := 0
    b := 0
    c := 0


  EVENT MLIn
  WEIGHT 1
  WHERE 
    0 < c
  THEN
    c := c - 1
  END

  EVENT MLOut
  WEIGHT 1
  WHERE 
    a + b < d /\
    c = 0
  THEN
    a := a + 1
  END

  EVENT ILIn
  WEIGHT 1
  WHERE 
    0 < a
  THEN
    a := a - 1
    b := b + 1
  END

  EVENT ILOut
  WEIGHT 1
  WHERE 
    0 < b /\
    a = 0 
  THEN
    a := b - 1 
    c := c + 1
  END

END

PROPERTIES
 a >= 0 
