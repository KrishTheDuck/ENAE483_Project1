from dataclasses import dataclass, field, asdict


@dataclass
class StageMass:
    #All units in kg
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

@dataclass
class RocketMass:
    """
    Calculate the mass of each stage of a two-stage rocket.
    The mass components considered for each stage include:
    """
    StageMass : StageMass
    PayloadFairing: float
    InterTankFairing: float
    InterStageFairing: float
    AftFairing: float