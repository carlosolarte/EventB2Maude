# Reader-writer example in Chapter 7 of Abrial's book #
# Abstract model #

CONTEXT ctxRW
SETS 
    D : { d0, d1, d2, d3, d4 }  # Data values #
CONSTANTS 
END

MACHINE RW
  SEES ctxRW
  VARIABLES
    w r 
    wt 
    #rd #
    f g

  INVARIANTS
    w  : Nat
    r  : Nat
    wt : Nat ** D
    # rd : Nat ** D #
    f  : Nat ** Nat
    g  : Nat ** Nat

  INITIALISATION
    w := 1
    r := 1
    wt := { 1 |-> d0 }
    # rd := { 1 |-> d0 } # 
    f  := { 1 |-> 1 }
    g  := { 1 |-> 1 }

  # Sending a block (not sent yet) to a client which is not currently receiving a block #
  EVENT write 
  WEIGHT 1
  ANY
   x <: {d0, d1, d2, d3, d4}
  WHERE 
    True
  THEN
    w := w + 1 
    wt := wt <+ { ( w + 1 )  |-> ( x ) }
  END

  # Receiving one block #
  EVENT read 
  WEIGHT 1  
  ANY 
    v <:  g(r) .. w 
  WHERE  
    True 
  THEN 
    r := r + 1  
    f := f <+ { (r + 1)  |-> (v) } 
    g := g <+ { (r + 1)  |-> (w) } 
    # rd := rd <+ { r |-> wt(v) } #  
  END 

END

PROPERTIES
 r
