from dataclasses import dataclass, field, asdict
import numpy as np

@dataclass
class StageMass:
    """
    Calculate the mass of a rocket stage.
    Contains various mass components and computes total and dry mass.
    """
    PropFu: float = 0.0 #Propellant Mass
    PropOx : float = 0.0 # Oxidizer Mass (if used)

    PropellantTank : float = 0.0 # Propellant Tank Mass
    PropellantTankInsulation: float = 0.0 # Propellant Tank Insulation Mass (cryogenic only)

    OxidizerTank : float = 0.0
    OxidizerTankInsulation : float = 0.0

    Engine : float = 0.0 #all except solid
    ThrustStructure : float = 0.0
    Casing: float = 0.0 #only if solid
    Gimbals: float = 0.0
    Avionics: float = 0.0
    Wiring: float = 0.0
    
    
    @property
    def TotalMass(self):
        """
        Total mass of the stage including propellant.
        """
        return np.nansum(np.array([self.PropFu, self.PropOx, self.PropellantTank, self.PropellantTankInsulation,
                self.OxidizerTank, self.OxidizerTankInsulation, self.Engine, self.ThrustStructure,
                self.Casing, self.Gimbals, self.Avionics, self.Wiring]))   
    
    @property
    def DryMass(self):
        """
        Dry mass of the stage excluding propellant.
        """
        return np.nansum(np.array([self.PropellantTank, self.PropellantTankInsulation,
                self.OxidizerTank, self.OxidizerTankInsulation, self.Engine, self.ThrustStructure,
                self.Casing, self.Gimbals, self.Avionics, self.Wiring]))  

@dataclass
class RocketMass:
    """
    Calculate the mass of each stage of a two-stage rocket.
    Contains 2 StageMass objects and fairing masses.
    """
    StageMass1 : StageMass
    StageMass2 : StageMass
    PayloadFairing: float
    InterTankFairing: float
    InterStageFairing: float
    AftFairing: float
    
    @property
    def TotalMass(self):
        """
        Total mass of the rocket including all stages and fairings.
        """
        return np.nansum(np.array([self.StageMass1.TotalMass, self.StageMass2.TotalMass, self.PayloadFairing, self.InterTankFairing,
                self.InterStageFairing, self.AftFairing]))
        
    @property
    def DryMass(self):
        """
        Dry mass of the rocket excluding wet mass (propellant/oxidizer masses).
        """
        return np.nansum(np.array([self.StageMass1.DryMass, self.StageMass2.DryMass, self.PayloadFairing, self.InterTankFairing,
                self.InterStageFairing, self.AftFairing]))