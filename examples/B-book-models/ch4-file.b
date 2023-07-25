# File transfer protocol (Chapter 4, Abrial's book)
# Abstract machine 
#
CONTEXT ctxFILE
SETS 
CONSTANTS 
    file : POW ( NAT ** NAT ) := { 1 |-> 1 , 2 |-> 2, 3 |-> 3 , 4 |-> 4} 
END


MACHINE FILE
  SEES ctxFILE

  VARIABLES
    fileRec # File at the receiver #
    b # termination

  INVARIANTS
    fileRec :  POW ( NAT ** NAT )
    b       :  Bool

  INITIALISATION

    fileRec    := emptyrel
    b          := False 

  
  EVENT final
  WEIGHT 1
  WHERE 
    b = False 
  THEN
    fileRec := file
    b := True
  END
END

PROPERTIES
 b
