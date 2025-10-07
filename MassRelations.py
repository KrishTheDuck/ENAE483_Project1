from RocketCase import RocketCase
from Engine import Engine
import numpy as np
from StageMass import StageMass,RocketMass  

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
    payload_diameter = 5.2
    payload_height = 13
    
    def __init__(self, X, R: RocketCase, D_outer: float, twr1, twr2):
        self.D_outer = D_outer # m, outer diameter of the rocket, assumed constant for both stages
        self.R = R
        self.X = X
        
        self.M1, self.M2 = self.R.findMasses(self.X)

        self.sm1, self.sm2 = StageMass(), StageMass()
        self.twr1, self.twr2 = twr1, twr2
        
        # ---------------------- Initialize oxidizer and fuel masses ----------------------
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
        # -----------------------------------------------------------------------------------
        # ---------------------- Get the propellant types from the name ---------------------
        s1_ox_type, s1_fuel_type = MassRelations.__get_propellants(R.engines[0].Name)
        s2_ox_type, s2_fuel_type = MassRelations.__get_propellants(R.engines[1].Name)
        # -----------------------------------------------------------------------------------
        
        # ---------------------- Find the tank masses, dimensions ----------------------
        self.sm1.OxidizerTank, self.sm1.OxidizerTankInsulation, self.sm1.PropellantTank, self.sm1.PropellantTankInsulation, self.S1Length= \
            self.__get_tank_masses(self.sm1, self.R.engines[0], s1_ox_type, s1_fuel_type)
        self.sm2.OxidizerTank, self.sm2.OxidizerTankInsulation, self.sm2.PropellantTank, self.sm2.PropellantTankInsulation, self.S2Length = \
            self.__get_tank_masses(self.sm2, self.R.engines[1], s2_ox_type, s2_fuel_type)
        # ------------------------------------------------------------------
        
        
        
        # ---------------------- Fairings, Make the RocketMass Object ---------------------
        # Aft Fairing
        aft_fairing_area = MassRelations.__aft_fairing_area(self.D_outer, self.D_outer/2) # ALL CAP DIAMETERS ARE EQUAL TO OUTER DIAMETER
        # Intertank (or interstage) Fairing
        intertank_fairing_area_stage1 = MassRelations.__interstage_fairing_area(self.D_outer/2, self.D_outer/2, self.S1Length[0] + self.S1Length[1])
        intertank_fairing_area_stage2 = MassRelations.__interstage_fairing_area(self.D_outer/2, self.D_outer/2, self.S2Length[0] + self.S2Length[1])
        # Payload Fairing
        payload_fairing_area = MassRelations.__payload_fairing_area(self.D_outer, self.D_outer/2, self.D_outer/2)
        # -----------------------------------------------------------------------------------
        # ---------------------- Fairing Masses ----------------------
        aft_fairing_mass = MassRelations.__fairing_mass(aft_fairing_area)
        intertank_fairing_mass_stage1 = MassRelations.__fairing_mass(intertank_fairing_area_stage1)
        intertank_fairing_mass_stage2 = MassRelations.__fairing_mass(intertank_fairing_area_stage2)
        payload_fairing_mass = MassRelations.__fairing_mass(payload_fairing_area)
        # ------------------------------------------------------------
        self.rm = RocketMass(StageMass1=self.sm1, StageMass2=self.sm2, PayloadFairing=payload_fairing_mass, InterTankFairing=intertank_fairing_mass_stage1 + intertank_fairing_mass_stage2, 
                        InterStageFairing= 0, AftFairing=aft_fairing_mass)
        
        
        
    
    def ReturnValues(self):
        return self.sm1, self.sm2
    
    def __get_length(self):
        S1len = 2.5*self.D_outer + 3 + sum(self.S1Length)
        S2Len = self.D_outer + self.__payload_fairing_length(self.D_outer)
        return (S1len, S2Len)

    def __get_tank_masses(self, SM, E: Engine, ox_type, fuel_type):
        if E.Density[0] != 0:
            ox_tank_l = (4/(np.pi*self.D_outer**2)) * (SM.PropOx / E.Density[0]) + self.D_outer #cylindrical tank length
        else: ox_tank_l = 0; #no oxidizer (solid)

        if E.Density[1] != 0:
            fu_tank_l = (4/(np.pi*self.D_outer**2)) * (SM.PropFu / E.Density[1]) + self.D_outer #cylindrical tank length
        else: fu_tank_l = 0; #no fuel -- this shouldnt happen

        Area_Ox = np.pi * self.D_outer * ox_tank_l + np.pi * self.D_outer ** 2 #surface area of cylinder + 2 hemispheres
        Area_Fu = np.pi * self.D_outer * fu_tank_l + np.pi * self.D_outer ** 2 #surface area of cylinder + 2 hemispheres

        match ox_type:
            case "LOX":
                ox_tank = 0.0107 * SM.PropOx
                ox_insulation = 1.123 * Area_Ox #from MERS slides -- only for LOX
            case "N2O4":
                #Hypergolic case -- annoying a fx of Prop volume not tank area
                ox_tank = 12.16*(SM.PropOx / E.Density[0])  #MERS slide 7
                ox_insulation = np.nan
            case None:
                #Solid only
                ox_tank = np.nan
                ox_insulation = np.nan
            case _:
                raise ValueError(f'Oxidizer "{ox_type}" not found')

        match fuel_type:
            case "LH2":
                fu_tank = 0.128 * SM.PropFu #why this formula? Do we want to consider Ti or COPV tanks?
                fu_insulation = 2.880 * Area_Fu
            case "RP1":
                fu_tank = 0.0148 * SM.PropFu
                fu_insulation = np.nan
            case "LCH4":
                fu_tank = 0.0287 * SM.PropFu
                fu_insulation = 1.123 * Area_Fu
            case "SOLID":
                fu_tank = SM.PropFu * 0.135
                fu_insulation = np.nan
            case "UDMH":
                fu_tank = 12.16*(SM.PropFu / E.Density[1])  #MERS slide 7
                fu_insulation = np.nan
            case _:
                raise ValueError(f'Fuel "{fuel_type}" not found')

        return ox_tank, ox_insulation, fu_tank, fu_insulation, (ox_tank_l, fu_tank_l)



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
    def __aft_fairing_area(D_outer, r_f):
        #Assume cylinder fairing
        return 2 * np.pi * D_outer * (r_f + 3) #3m for engine length

    @staticmethod
    def __interstage_fairing_area(r1, r2, h):
        #Assume frustrum fairing
        return np.pi * (r1 + r2) * np.sqrt((r1-r2)** 2 + h**2)

    @staticmethod
    def __payload_fairing_area(D_outer, r_ox, r_f):
        # Max diameter of tanks. First pass we set the diameter, second pass we change tank sizes
        RocketRadius = max(r_ox,r_f,D_outer/2)
        
        rc = MassRelations.payload_diameter / 2 # m, radius of the payload
        h = (r_ox + MassRelations.payload_height)        # m, height of the payload
        
        h1 = (h * rc) / (RocketRadius - rc)
        
        #Assume conical fairing
        return np.pi * D_outer * np.sqrt((D_outer/2)**2 + (h+h1)**2)
    
    @staticmethod
    def __payload_fairing_length(D_outer):
        # Max diameter of tanks. First pass we set the diameter, second pass we change tank sizes
        RocketRadius =  D_outer/2

        rc = MassRelations.payload_diameter / 2  # m, radius of the payload
        h = (RocketRadius + MassRelations.payload_height)  # m, height of the payload

        h1 = (h * rc) / (RocketRadius - rc)
        # Assume conical fairing
        return h1 + h


    @staticmethod
    def __fairing_mass(area):
        #Fairing mass as a function of area
        return 4.95 * area ** 1.15
    
    @staticmethod
    def __avionics_mass(M0):
        #Avionics mass as a function of gross mass
        return 10 * M0 ** 0.361

    @staticmethod
    def __wiring_mass(M0, TotalLength):
        #Wiring mass as a function of gross mass
        return 1.058 * np.sqrt(M0) * TotalLength ** 0.25

    def __getPropulsion_Sys_Mass(self, E =(Engine,Engine)):
        #Inputs: Engine class, Masses dict, Stage index (0 or 1)

        #M_engine = f(Thrust,Ae,At) Liquid
        #M_casing = f(M_prop) Solid
        #M_thrust_struct = f(Thrust) Both

        # Calculate Engines required. 
        # first stage carries literally everything.
        Masses = [self.sm1, self.sm2]
        m01 = Masses[0].TotalMass + Masses[1].TotalMass + self.R.mPL
        m02 = Masses[1].TotalMass + self.R.mPL
        
                
        # Calculate number of engines required given a twr for both stages.
        n_engines_s1 = m01 * 9.81 * self.twr1 / (E[0].Fn[0] * 1e6)  #number of engines on stage 1
        n_engines_s2 = m02 * 9.81 * self.twr2 / (E[1].Fn[1] * 1e6)  #number of engines on stage 2
        
        n_thruster = (np.ceil(n_engines_s1), np.ceil(n_engines_s2))
        
        #Lambda functions for the mass relations
        M_engine = lambda T,NozzleRatio,N: (7.81e-4 * N*T*1e6 * 3.37e-5 * N*T*1e6 * np.sqrt(NozzleRatio) + 59) #kg, MERS slide 27
        M_casing = lambda M_prop: 0.135*M_prop #kg, MERS slide 27 -- SOLID ONLY
        M_thrust_struct = lambda T,N: 2.55e-4 * T*1e6 * N#kg, MERS slide 27
        M_gimbals = lambda T,P0,N: (237.8 * (N*T/P0)**(0.9375)) #kg, MERS slide 28

        for n in range(0,2):
            match E[n].Name:
                case "SOLID":
                    Masses[n].Casing = M_casing(Masses[n].PropFu)
                    Masses[n].Engine = np.nan
                case _:
                    Masses[n].Casing = np.nan
                    Masses[n].Engine = M_engine(E[n].Fn[n],E[n].NozzleRatio[n],n_thruster[n])

            Masses[n].ThrustStructure = M_thrust_struct(E[n].Fn[n],n_thruster[n])
            Masses[n].Gimbals = M_gimbals(E[n].Fn[n],E[n].p[n],n_thruster[n])

        return Masses[0],Masses[1], n_thruster
