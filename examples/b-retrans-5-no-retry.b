# Bounded re-transmission protocol (Chapter 6, Abrial's book)
# 5th refinement of the model  #
# The content of the file is irrelevant. Hence, d always take the value D2

CONTEXT ctxBRTP
SETS 
    STATE : {working, success, failure }
    DATA  : { D1 , D2 } 
CONSTANTS 
    N : Nat := 20    # Size of the file #
    MAX : Nat := 20   # Number of retries #
END

MACHINE BRTP
  SEES ctxBRTP

  VARIABLES
    r       # Counter for the receiver 
    g       # File at the receiver 
    rst sst # states for the receiver and the sender 
    s       # Counter at the receiver 
    d       # Data to be transmitted
    # Activation bits  
    w db ab v l
    c       # Current number of retries 
    t       # number of sends

  INVARIANTS
    r          : Nat 
    g          : POW ( Nat ** STATE )
    rst        : STATE 
    sst        : STATE 
    s          : Nat 
    d          : DATA
    w          : Bool 
    db         : Bool
    ab         : Bool
    v          : Bool 
    l          : Bool 
    c          : Nat 
    t          : Nat

  INITIALISATION
    r          := 0
    g          := emptyrel
    rst        := working 
    sst        := working 
    s          := 0
    d          := D1
    w          := True 
    db         := False
    ab         := False
    v          := False
    l          := False
    c          := 0
    t          := 0

  EVENT SNDsndcurrentdata
  WEIGHT 1
  WHERE 
    sst = working /\
    w = True /\
    s + 1 < N
  THEN
    d := D2
    w := False
    db := True
    l := False
    t := t + 1
  END

  EVENT SNDsndlastdata
  WEIGHT 1
  WHERE 
    sst = working /\
    w = True /\
    s + 1 = N
  THEN
    d := D2
    w := False
    db := True
    l := True
    t := t + 1
  END

  EVENT RCVrcvcurdata
  WEIGHT 1
  WHERE 
    rst = working /\
    db = True /\
    r = s /\
    l = False
  THEN
    r := r + 1
    g := g <+ { r  |-> d }
    db := False
    v := True
  END

  EVENT RCVsuccess
  WEIGHT 1
  WHERE 
    rst = working /\
    db = True /\
    r = s /\
    l = True
  THEN
    rst := success 
    r := r + 1
    g := g <+ { r  |-> d }
    db := False
    v := True
  END

  EVENT RCVrcvretry
  WEIGHT 9
  WHERE 
    db = True /\
    r <> s 
  THEN
    db := False
    v := True
  END

  EVENT RCVsndack
  WEIGHT 9
  WHERE 
    v = True 
  THEN
    v := False
    ab := True
  END

  EVENT SNDrcvcuracl
  WEIGHT 9
  WHERE 
    sst = working /\
    ab = True /\
    s + 1 < N
  THEN
    w := True
    s := s + 1
    ab := False
  END

  EVENT SNDsuccess
  WEIGHT 9
  WHERE 
    sst = working /\
    ab = True /\
    s + 1 = N
  THEN
    sst := success
    ab := False
  END

  EVENT DMNdatach
  WEIGHT 1
  WHERE 
    db = True
  THEN
    db := False
  END

  EVENT DMNack
  WEIGHT 1
  WHERE 
    ab = True
  THEN
    ab := False
  END

  EVENT SNDtimeout
  WEIGHT 1
  WHERE 
    sst = working /\
    w = False /\
    ab = False /\
    db = False /\
    v = False
  THEN
    w := True
    c := c + 1
  END
END

PROPERTIES
 sst = failure /\ rst = failure   ;
 sst = success /\ rst = success 
