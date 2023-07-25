# File transfer protocol (Chapter 4, Abrial's book)
# 2nd Refinement 
#
CONTEXT ctxFILE
SETS 
CONSTANTS 
    file : POW ( NAT ** NAT ) := { 1 |-> 1 , 2 |-> 2, 3 |-> 3 , 4 |-> 4} 
    N    : NAT  :=  4 
END


MACHINE FILE
  SEES ctxFILE

  VARIABLES
    fileRec # File at the receiver #
    b # termination
    s # Counter at the sender
    r # Counter at the receiver 
    d # datum 


  INVARIANTS
    fileRec :  POW ( NAT ** NAT )
    b       :  Bool
    s       :  NAT 
    r       :  NAT 
    d       :  NAT 

  INITIALISATION

    fileRec    := emptyrel
    b          := False 
    s          := 1 
    r          := 1 
    d          := 0

  
  EVENT final
  WEIGHT 1
  WHERE 
    b = False /\
    r = N + 1 
  THEN
    b := True
  END

  EVENT receive
  WEIGHT 1
  WHERE 
    s = r + 1 
  THEN
    fileRec := fileRec \s/ { ( r ) |-> ( d ) } 
    r       := r + 1 
  END

  EVENT send 
  WEIGHT 1
  WHERE 
    s = r /\
    r <> N + 1
  THEN
    d       := file(s)
    s       := s + 1
  END

END

PROPERTIES
 b ; 
 s ; 
 r 
