from dataclasses import dataclass, field

@dataclass(frozen=True)
class Engine:
  """
    FMMR         - Fuel-Mixture Mass Ratio
    Isp          - Specific Impulse
    
    --- The following are indexed w.r.t the stage i.e. stage1 is 0 stage2 is 1 ----
    Fn           - Thrust
    Ae           - Nozzle Exhaust Area
    p            - Stagnation Pressure / Chamber Pressure
    NozzleRatio  - Nozzle Expansion Ratio
    Density      - Density for [oxidizer, propellant]
    Name        - Used for plotting titles
    -------------------------------------------------------------------------------
  """
  FMMR : float
  Isp : float
  Fn : tuple[float,float]
  Ae : tuple[float,float]
  p : tuple[float,float]
  NozzleRatio : tuple[float,float]
  Density : tuple[float,float]
  Name : str #names of propellant (used for plotting)