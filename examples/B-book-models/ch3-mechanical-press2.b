# 2nd Model Mechanical-press system #
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
    startmotorB
    stopmotorB
    startmotorI
    stopmotorI

  INVARIANTS

    motoract    : STATUS
    motorsen    : STATUS
    startmotorB : Bool
    stopmotorB  : Bool
    startmotorI : Bool
    stopmotorI  : Bool

  INITIALISATION

    motoract    := stopped
    motorsen    := stopped
    startmotorB := False
    stopmotorB  := False
    startmotorI := False
    stopmotorI  := False


  EVENT PushStartMotorB
  WEIGHT 1
  WHERE 
    startmotorB = False
  THEN
    startmotorB := True 
  END

  EVENT ReleaseStartMotorB
  WEIGHT 1
  WHERE 
    startmotorB = True
  THEN
    startmotorB := False 
  END

  EVENT StartMotor
  WEIGHT 1
  WHERE 
    motoract = stopped /\
    motorsen = stopped /\
    startmotorI = False /\
    startmotorB = True 

  THEN
    startmotorI := True
    motoract    := working
  END

  EVENT TReleaseStartMotorB
  WEIGHT 1
  WHERE 
    startmotorI = True /\ 
    startmotorB = False
  THEN
    startmotorI := False 
  END

  EVENT PushStopMotorB
  WEIGHT 1
  WHERE 
    stopmotorB = False
  THEN
    stopmotorB := True
  END

  EVENT ReleaseStopMotorB
  WEIGHT 1
  WHERE 
    stopmotorB = True
  THEN
    stopmotorB := False
  END

  EVENT StopMotor
  WEIGHT 1
  WHERE 
    stopmotorI = False /\
    stopmotorB = True /\
    motoract = working /\
    motorsen = working
  THEN
    motoract := stopped  
    stopmotorI := True 
  END

  EVENT TreatReleaseStopMotorB
  WEIGHT 1
  WHERE 
    stopmotorI = True /\
    stopmotorB = False 
  THEN
    stopmotorI := False 
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

  EVENT PushButtonMotorFalse
  WEIGHT 1
  WHERE 
    startmotorI = False /\
    startmotorB = True /\
    (motoract = working \/ motorsen = working)
  THEN
    startmotorI := True
  END

END

PROPERTIES
 motorsen = working 
