from RocketCase import RocketCase
from Engine import Engine
import numpy as np
from StageMass import StageMass


class MassRelations:
    """
    2.1. Create a Systems-Level Analysis Tool (Group). Using a first stage ∆V fraction as an
    input variable and the mass estimating relations from class, create a script that returns the masses
    for each sub-system in a stage. This will sum to the mass for each stage. You will be finding
    the two total stage masses, summing those to the total gross mass for the launch vehicle, and
    comparing this number to the solutions found in the vehicle-level design section.

    Include mass estimates for each of the following sub-systems:

    •Propellant
    •Propellant tanks
    •Propellant tank insulation (cryogen propellants need insulation, others do not)
    •Engines (except for solid)
    •Thrust structure
    •Casing (only if solid)
    •Gimbals
    •Avionics
    •Wiring
    •Payload fairing (make it aerodynamic!)
    •Inter-tank fairing
    •Inter-stage fairing
    •Aft fairing (*Leave sufficient engine fairing below the propellant tanks of each stage to
    accommodate the engines. Assume the engines are 3m long

    """

    def __init__(self, X, R: RocketCase):
        self.R = R
        self.X = X

        self.M1, self.M2 = self.R.findMasses(self.X)

        self.sm1, self.sm2 = StageMass, StageMass

        # Stage 1
        self.sm1.PropOx = self.M1["m_pr"] * (
            self.R.engines[0].FMMR / (self.R.engines[0].FMMR + 1)
        )  # oxidizer mass
        self.sm1.PropFu = self.M1["m_pr"] * (
            1 / (self.R.engines[0].FMMR + 1)
        )  # fuel mass

        # Stage 2
        self.sm2.PropOx = self.M2["m_pr"] * (
            self.R.engines[1].FMMR / (self.R.engines[1].FMMR + 1)
        )  # oxidizer mass
        self.sm2.PropFu = self.M2["m_pr"] * (
            1 / (self.R.engines[1].FMMR + 1)
        )  # fuel mass

        s1_ox_type, s1_fuel_type = MassRelations.__get_propellants(R.engines[0].Name)
        s2_ox_type, s2_fuel_type = MassRelations.__get_propellants(R.engines[1].Name)

        self.sm1.OxidizerTank, self.sm1.OxidizerTankInsulation, \
            self.sm1.PropellantTank, self.sm1.PropellantTankInsulation = (
            MassRelations.__get_tank_masses(
                self.M1, self.R.engines[0], s1_ox_type, s1_fuel_type
            )
        )

    @staticmethod
    def __get_propellants(name: str):
        # Split the propellant name into oxidizer and fuel
        if "-" in name:
            oxidizer, fuel = name.split("-", 1)
            return oxidizer, fuel
        else:
            # No dash: only fuel present
            return None, name

    @staticmethod
    def __get_tank_masses(Masses, E: Engine, ox_type, fuel_type):
        ox_tank = 0.0107 * Masses["m_ox"]

        # add n2o4 optimization?
        ox_tank_r = ((Masses["m_ox"] / E.Density[0]) / (4 * np.pi / 3)) ^ (1 / 3)
        fu_tank_r = ((Masses["m_fu"] / E.Density[1]) / (4 * np.pi / 3)) ^ (1 / 3)

        Area_Ox = 4 * np.pi * ox_tank_r ^ 2
        Area_Fu = 4 * np.pi * fu_tank_r ^ 2

        ox_insulation = 1.123 * Area_Ox

        match fuel_type:
            case "LH2":
                fu_tank = 0.128 * Masses["m_fu"]
                fu_insulation = 2.880 * Area_Fu
            case "RP1":
                fu_tank = 0.0148 * Masses["m_fu"]
                fu_insulation = np.nan
            case "LCH4":
                fu_tank = 0.0287 * Masses["m_fu"]
                fu_insulation = 1.123 * Area_Fu
            case "Solid":
                fu_tank = Masses["m_fu"] * 0.135
                fu_insulation = np.nan
            case "UDMH":
                fu_tank = np.nan  # how do i do udmh???
                fu_insulation = np.nan
            case _:
                raise ValueError(f'Fuel "{fuel_type}" not found')

        return ox_tank, ox_insulation, fu_tank, fu_insulation

    # Suppose we have the tanks as spheres here.
    # if ox_tank_r is not np.nan:
    # To make it aerodynamic we need to find the best cone shape at mach ~20+
    # Best in this case is the shape that minimizes energy dissipation by the flow i.e., the one
    # where the engine doesn't have to work as hard to push through the air.
    #
    # The work done by the engine to push against the air and gravity is dissipated in hypersonic regimes
    # by the shock-induced drag/wave drag longer cones would decrease shock-induced drag.
    # Newtonian estimation of drag coefficient at high mach: 2 sin(theta)^2 / (gamma * M^2).
    # sin(theta) is then r/(2 * sqrt(r^2 + h^2))
    # So we minimize Cost = r/(sqrt(r^2 + h^2)) / (gamma * M^2) + Area, wrt height
    # => r * (-1/2) * (r^2 + h^2) ^ (-3/2) * (2 * h) * 1/(gamma * M^2) + pi * r * h / sqrt(r^2 + h^2) = 0
    # =>  -(r^2 + h^2) ^ (-1) * 1/(gamma * M^2) + pi = 0
    # => sqrt((pi * gamma * M^2)^-1 - r^2) = h
    # say gamma is like 1.2, M is like 20 ish. then

    # payload_area = np.pi * ox_tank_r * np.sqrt(ox_tank_r ** 2 + h ** 2);
