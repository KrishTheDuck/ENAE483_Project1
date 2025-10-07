from dataclasses import dataclass, field, asdict
import numpy as np

@dataclass
class StageMass:
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
        return np.nansum(np.array([self.PropFu, self.PropOx, self.PropellantTank, self.PropellantTankInsulation,
                self.OxidizerTank, self.OxidizerTankInsulation, self.Engine, self.ThrustStructure,
                self.Casing, self.Gimbals, self.Avionics, self.Wiring]))   
    
    @property
    def DryMass(self):
        return np.nansum(np.array([self.PropellantTank, self.PropellantTankInsulation,
                self.OxidizerTank, self.OxidizerTankInsulation, self.Engine, self.ThrustStructure,
                self.Casing, self.Gimbals, self.Avionics, self.Wiring]))  

@dataclass
class RocketMass:
    """
    Calculate the mass of each stage of a two-stage rocket.
    The mass components considered for each stage include:
    """
    StageMass1 : StageMass
    StageMass2 : StageMass
    PayloadFairing: float
    InterTankFairing: float
    InterStageFairing: float
    AftFairing: float
    
    @property
    def TotalMass(self):
        return np.nansum(np.array([self.StageMass1.TotalMass, self.StageMass2.TotalMass, self.PayloadFairing, self.InterTankFairing,
                self.InterStageFairing, self.AftFairing]))
        
    @property
    def DryMass(self):
        return np.nansum(np.array([self.StageMass1.DryMass, self.StageMass2.DryMass, self.PayloadFairing, self.InterTankFairing,
                self.InterStageFairing, self.AftFairing]))