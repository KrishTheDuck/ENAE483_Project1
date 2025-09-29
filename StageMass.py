from dataclasses import dataclass, field


@dataclass(frozen=True)
class StageMass:
    #All units in kg
    PropFu: float #Propellant Mass
    PropOx : float # Oxidizer Mass (if used)

    PropellantTank : float # Propellant Tank Mass
    PropellantTankInsulation: float # Propellant Tank Insulation Mass (cryogenic only)

    OxidizerTank : float
    OxidizerTankInsulation : float
    
    Engine : float #all except solid
    ThrustStructure : float
    Casing: float #only if solid
    Gimbals: float
    Avionics: float
    Wiring: float
    PayloadFairing: float
    InterTankFairing: float
    InterStageFairing: float
    AftFairing: float