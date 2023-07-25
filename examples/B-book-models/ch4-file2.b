# File transfer protocol (Chapter 4, Abrial's book)
# 1st Refinement 
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
    counter # Counter at the receiver 

  INVARIANTS
    fileRec :  POW ( NAT ** NAT )
    b       :  Bool
    counter :  NAT 

  INITIALISATION

    fileRec    := emptyrel
    b          := False 
    counter    := 1 

  
  EVENT final
  WEIGHT 1
  WHERE 
    b = False /\
    counter = N + 1 
  THEN
    b := True
  END

  EVENT receive
  WEIGHT 1
  WHERE 
    counter <= N 
  THEN
    fileRec := fileRec \s/ { ( counter ) |-> ( file(counter) ) } 
    counter := counter + 1 
  END

END

PROPERTIES
 b
