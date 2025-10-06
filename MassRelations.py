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

    def __init__(self, X, R: RocketCase,D_outer = 4):
        self.D_outer = D_outer #m, outer radius of the rocket, assumed constant for both stages
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

        self.sm1.OxidizerTank, self.sm1.OxidizerTankInsulation, self.sm1.PropellantTank, self.sm1.PropellantTankInsulation = (
            MassRelations.__get_tank_masses(self.M1, self.R.engines[0], s1_ox_type, s1_fuel_type)
        )
            
        self.sm2.OxidizerTank, self.sm2.OxidizerTankInsulation, self.sm2.PropellantTank, self.sm2.PropellantTankInsulation = (
            MassRelations.__get_tank_masses(self.M2, self.R.engines[1], s2_ox_type, s2_fuel_type)
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


    def __get_tank_masses(self,Masses, E: Engine, ox_type, fuel_type):
        # add n2o4 optimization?
        ox_tank_l = (4/(np.pi*self.D_outer^2))*(Masses["m_ox"] / E.Density[0]) + (2/3)*self.D_outer #cylindrical tank length
        fu_tank_l = (4/(np.pi*self.D_outer^2))*(Masses["m_fu"] / E.Density[1]) + (2/3)*self.D_outer #cylindrical tank length

        Area_Ox = np.pi * self.D_outer * ox_tank_l + np.pi * self.D_outer ^ 2 #surface area of cylinder + 2 hemispheres
        Area_Fu = np.pi * self.D_outer * fu_tank_l + np.pi * self.D_outer ^ 2 #surface area of cylinder + 2 hemispheres

        match ox_type:
            case "LOX":
                ox_tank = 0.0107 * Masses["m_ox"]
                ox_insulation = 1.123 * Area_Ox #from MERS slides -- only for LOX
            case "N2O4":
                #Hypergolic case -- annoying a fx of Prop volume not tank area
                ox_tank = 12.16*(Masses["m_ox"] / E.Density[0])  #MERS slide 7
                ox_insulation = np.nan
            case None:
                #Solid only
                ox_tank = np.nan
                ox_insulation = np.nan
            case _:
                raise ValueError(f'Oxidizer "{ox_type}" not found')

        match fuel_type:
            case "LH2":
                fu_tank = 0.128 * Masses["m_fu"] #why this formula? Do we want to consider Ti or COPV tanks?
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
                fu_tank = 12.16*(Masses["m_fu"] / E.Density[1])  #MERS slide 7
                fu_insulation = np.nan
            case _:
                raise ValueError(f'Fuel "{fuel_type}" not found')

        return ox_tank, ox_insulation, fu_tank, fu_insulation

    def __getPropulsion_Sys_Mass(self, E: Engine, Masses):
        #M_engine = f(Thrust,Ae,At) Liquid
        #M_casing = f(M_prop) Solid
        #M_thrust_struct = f(Thrust) Both

        #Lambda functions for the mass relations
        M_engine = lambda T,NozzleRatio: 7.81e-4 * T * 3.37e-5 * T * np.sqrt(NozzleRatio) + 59 #kg, MERS slide 27
        M_casing = lambda M_prop: 0.135*M_prop #kg, MERS slide 27 -- SOLID ONLY
        M_thrust_struct = lambda T: 2.55e-4 * T #kg, MERS slide 27
        M_gimbals = lambda T,P0: 237.8 * (T/P0)^(0.9375) #kg, MERS slide 28

        #todo working on this rn
        match E.Name:
            case "SOLID":
                pass
            case _:
                pass


        return M_rocket_engine, M_casing, M_thrust_struct, M_gimbals

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
