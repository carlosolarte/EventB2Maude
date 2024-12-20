# 1st Model Mechanical-press system #
# Chapter 3 Abrial's book #
#
CONTEXT ctxMechanicalPress
SETS 
    STATUS : { stopped, working  }
CONSTANTS 
END

MACHINE MechanicalPressSystem
  SEES ctxMechanicalPress

  VARIABLES

    motoract
    motorsen

  INVARIANTS

    motoract : STATUS
    motorsen : STATUS

  INITIALISATION

    motoract := stopped
    motorsen := stopped


  EVENT StartMotor
  WEIGHT 1
  WHERE 
    motoract = stopped /\
    motorsen = stopped
  THEN
    motoract := working 
  END

  EVENT StopMotor
  WEIGHT 1
  WHERE 
    motoract = working /\
    motorsen = working
  THEN
    motoract := stopped  
  END

  EVENT MotorStart
  WEIGHT 1
  WHERE 
    motorsen = stopped /\
    motoract = working  
  THEN
    motorsen := working 
  END

  EVENT MotorStop
  WEIGHT 1
  WHERE 
    motorsen = working /\
    motoract = stopped 
  THEN
    motorsen := stopped 
  END
END

PROPERTIES
 motorsen = working 
