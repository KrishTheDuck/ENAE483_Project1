from dataclasses import dataclass, field

@dataclass(frozen=True)
class Engine:
  """The Engine class is a dataclass that stores information about a propellant mixture. The object must be instantiated with the following values:
    
    :param FMMR: Fuel-Mixture Mass Ratio                      
    :type FMMR: float
    
    :param Isp: Specific Impuse
    :type Isp: float
    
    :param Fn: Thrust
    :type Fn: Tuple[float,float]
    
    :param p: Chamber Pressures
    :type p: Tuple[float,float]
    
    :param NozzleRatio: Nozzle Expansion Ratio
    :type NozzleRatio: Tuple[float,float]
    
    :param Density: Propellant mixture densities for the oxidizer and propellant - (oxidizer density, propellant density)
    :type Density: Tuple[float,float]

    :param Name: Name of the Propellant mixture
    :type Name: str
  """
  FMMR : float
  Isp : float
  Fn : tuple[float,float]
  Ae : tuple[float,float]
  p : tuple[float,float]
  NozzleRatio : tuple[float,float]
  Density : tuple[float,float]
  Name : str #names of propellant (used for plotting)