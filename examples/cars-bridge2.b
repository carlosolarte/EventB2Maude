# Second refinement car-bridge system #
# Chapter 1: Abrial's book #
#
CONTEXT ctxCarBridge
SETS 
    COLOR : {red, green }
CONSTANTS 
    d : Nat := 10
END

MACHINE CarBridgeSystem
  SEES ctxCarBridge

  VARIABLES

    a b c 
    mltl iltl mlpass ilpass

  INVARIANTS

    a      : Nat
    b      : Nat
    c      : Nat
    mltl   : COLOR
    iltl   : COLOR
    mlpass : Bool
    ilpass : Bool

  INITIALISATION

    a := 0
    b := 0
    c := 0
    mltl := green
    iltl := red 
    mlpass := False
    ilpass := True 



  EVENT MLOut1
  WEIGHT 1
  WHERE 
    mltl = green /\
    a + b + 1 <> d
  THEN
    a := a + 1
    mlpass := True
  END

  EVENT MLOut2
  WEIGHT 1
  WHERE 
    mltl = green /\
    a + b + 1 = d
  THEN
    a := a + 1
    mltl := red
    mlpass := True
  END

  EVENT ILOut1
  WEIGHT 1
  WHERE 
    iltl = green /\
    b <> 1
  THEN
    b := b - 1
    c := c + 1
    ilpass := True
  END

  EVENT ILOut2
  WEIGHT 1
  WHERE 
    iltl = green /\
    b = 1
  THEN
    b := b - 1
    c := c + 1
    iltl := red 
    ilpass := True
  END


  EVENT MLIn
  WEIGHT 1
  WHERE 
    0 < c
  THEN
    c := c - 1
  END

  EVENT ILIn
  WEIGHT 1
  WHERE 
    0 < a
  THEN
    a := a - 1
    b := b + 1
  END

  EVENT MLTlGreen
  WEIGHT 1
  WHERE 
    mltl = red /\
    a + b < d /\
    c = 0 /\
    ilpass = True
  THEN
    mltl := green
    iltl := red 
    mlpass := False
  END

  EVENT ILTlGreen
  WEIGHT 1
  WHERE 
    iltl = red /\
    0 < b /\
    a = 0 /\
    mlpass = True
  THEN
    iltl := green
    mltl := red 
    ilpass := False
  END

END

PROPERTIES
 a >= 0 
