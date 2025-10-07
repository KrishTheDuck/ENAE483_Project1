from Engine import Engine
from RocketCase import RocketCase
import matplotlib.pyplot as plt
import Solver as S
import MassRelations
from dataclasses import asdict
import numpy as np

from StageMass import StageMass, RocketMass

def S2ndStage(Stage1Prop,Stage2Prop):
    #PARAMS
    dVtot = 12.3e3 #in m/s since all the rest of my calculations use base SI units
    mPL = 26000 #kg
    delta1 = 0.08
    delta2 = 0.08
    #SETUP
    R = RocketCase(dVtot,mPL,(delta1,delta2),(Stage1Prop,Stage2Prop))
    Sol = S.Solver(R)

    #SOlutions
    X_mass, m0_mass, St_mass, fig_mass = Sol.MinimumMass()  # returns minimum mass solution (with plot)
    X_cost, Costs, (m1_cost, m2_cost), fig_cost = Sol.MinimumCost() #returns minimum cost solution (with plot)

    # Print summary for this propellant combo
    print(f"--- S1: {Stage1Prop.Name}, S2: {Stage2Prop.Name} ---")
    print(f"Minimum Mass Solution:")
    print(f"  dV fraction in Stage 1 (X): {X_mass:.3g}")
    print(f"  Overall LV mass: {m0_mass:.3g} metric tonnes")
    total_cost_mass = (R.findCost(St_mass[0]["m_in"]) + R.findCost(St_mass[1]["m_in"]))/1000
    print(f"  LV Cost: {total_cost_mass:.3g} B2025")
    print(f"Minimum Cost Solution:")
    print(f"  dV fraction in Stage 1 (X): {X_cost:.3g}")
    print(f"  Overall LV mass: {(m1_cost['m0'])/1000:.3g} metric tonnes")
    print(f"  Overall LV cost: ${Costs[0]/1000:.3g} B2025")
    print()

    plt.show()

def Submission2(Stage1, Stage2):
    # PARAMS
    dVtot = 12.3e3  # m/s
    mPL = 26000  # kg
    delta1 = 0.08
    delta2 = 0.08
    X = 0.586  # dV fraction in stage 1
    D_outer = 9  # m, initial guess
    TOL = 1e-3  # 0.1% tolerance for convergence
    mass_margin_frac = 0.5  # 30% mass margin
    max_iter = 100
    min_ld = 13
    ld_step = 0.25  # m, increment for diameter if L/D too high
    max_engines = 100  # safety cap

    converged = False
    prev_total_mass = None

    # Start with minimum engines for each stage
    n_engines_1 = 1
    n_engines_2 = 1

    for iteration in range(max_iter):
        # Calculate required thrust for TWR
        # We'll iterate n_engines for each stage until TWR is met
        twr1_met = False
        twr2_met = False
        inner_iter = 0
        while not (twr1_met and twr2_met) and inner_iter < max_iter:
            # Set up MassRelations with current n_engines
            # We'll pass TWR requirements to MassRelations, which should use them to set n_thrusters
            R = RocketCase(dVtot, mPL, (delta1, delta2), (Stage1, Stage2))
            M = MassRelations.MassRelations(X, R, D_outer, 1.3, 0.76)
            # Overwrite n_thrusters with our current guess
            M.n_thrusters = (n_engines_1, n_engines_2)
            SM1, SM2 = M.ReturnValues()

            # Add 30% mass margin
            total_mass_nomargin = SM1.TotalMass + SM2.TotalMass + mPL
            total_mass = total_mass_nomargin * (1 + mass_margin_frac)
            mass_margin = (total_mass - total_mass_nomargin) / total_mass

            # TWR calculations
            g0 = 9.81
            thrust_1 = n_engines_1 * Stage1.Fn[0] * 1e6  # N
            thrust_2 = n_engines_2 * Stage2.Fn[1] * 1e6  # N
            twr_stage_1 = thrust_1 / (SM1.TotalMass * g0)
            twr_stage_2 = thrust_2 / (SM2.TotalMass * g0)

            twr1_met = twr_stage_1 >= 1.3
            twr2_met = twr_stage_2 >= 0.76

            if not twr1_met:
                n_engines_1 += 1
                if n_engines_1 > max_engines:
                    print("Stage 1: Exceeded max engines, cannot meet TWR requirement.")
                    break
            if not twr2_met:
                n_engines_2 += 1
                if n_engines_2 > max_engines:
                    print("Stage 2: Exceeded max engines, cannot meet TWR requirement.")
                    break
            inner_iter += 1

        # L/D calculations (total rocket)
        S1_length = sum(M.S1Length) if hasattr(M, 'S1Length') else float('nan')
        S2_length = sum(M.S2Length) if hasattr(M, 'S2Length') else float('nan')
        total_length = S1_length + S2_length
        ld_total = total_length / D_outer if D_outer else float('nan')

        # Print iteration summary
        print(f"\nIteration {iteration+1}")
        print(f"Total Rocket Mass (with 30% margin): {total_mass/1e3:.3g} metric tonnes")
        print(f"Mass Margin: {mass_margin:.2%}")
        print(f"Stage 1 TWR: {twr_stage_1:.3f} (Required: >= 1.3)")
        print(f"Stage 2 TWR: {twr_stage_2:.3f} (Required: >= 0.76)")
        print(f"Total L/D: {ld_total:.3f} (Required: <= 13)")
        print(f"Diameter: {D_outer:.3f} m")
        print(f"Number of Engines: Stage 1 = {n_engines_1}, Stage 2 = {n_engines_2}")
        if twr_stage_1 < 1.3:
            print(f"  Warning: Stage 1 TWR below requirement!")
        if twr_stage_2 < 0.76:
            print(f"  Warning: Stage 2 TWR below requirement!")
        if ld_total > min_ld:
            print(f"  Warning: Total L/D above requirement!")

        # Adjust D_outer if L/D too high
        if ld_total > min_ld:
            D_outer += ld_step
            continue

        # Check for convergence (mass only, since requirements are enforced above)
        if prev_total_mass is not None:
            rel_change = abs(total_mass - prev_total_mass) / prev_total_mass
            if rel_change < TOL:
                converged = True
                print("\nConverged!")
                break
        prev_total_mass = total_mass

    if not converged:
        print("\nWarning: Did not converge within max iterations.")

    # Final summary
    print("\n--- Final Design Summary ---")
    print(f"Total Rocket Mass (with 30% margin): {total_mass/1e3:.3g} metric tonnes")
    print(f"Stage 1 TWR: {twr_stage_1:.3f}")
    print(f"Stage 2 TWR: {twr_stage_2:.3f}")
    print(f"Total L/D: {ld_total:.3f}")
    print(f"Number of Engines: Stage 1 = {n_engines_1}, Stage 2 = {n_engines_2}")
    print(f"Stage 1 Length: {S1_length:.3f} m")
    print(f"Stage 2 Length: {S2_length:.3f} m")
    print(f"Total Length: {total_length:.3f} m")
    print(f"Diameter: {D_outer:.3f} m")
    print(f"Payload: {mPL:.3f} kg")
    print(f"Mass Margin: {mass_margin:.2%}")
    print("(Check warnings above for any requirement violations.)")

    # Detailed mass breakdown (all in kg)
    print("\n--- Mass Breakdown (kg) ---")
    print("Stage 1:")
    print(f"  Propellant Ox: {SM1.PropOx:.3f}")
    print(f"  Propellant Fu: {SM1.PropFu:.3f}")
    print(f"  Oxidizer Tank: {SM1.OxidizerTank:.3f}")
    print(f"  Propellant Tank: {SM1.PropellantTank:.3f}")
    print(f"  Oxidizer Tank Insulation: {SM1.OxidizerTankInsulation:.3f}")
    print(f"  Propellant Tank Insulation: {SM1.PropellantTankInsulation:.3f}")
    print(f"  Engine: {SM1.Engine:.3f}")
    print(f"  Thrust Structure: {SM1.ThrustStructure:.3f}")
    print(f"  Casing: {SM1.Casing:.3f}")
    print(f"  Gimbals: {SM1.Gimbals:.3f}")
    print(f"  Avionics: {SM1.Avionics:.3f}")
    print(f"  Wiring: {SM1.Wiring:.3f}")
    print("Stage 2:")
    print(f"  Propellant Ox: {SM2.PropOx:.3f}")
    print(f"  Propellant Fu: {SM2.PropFu:.3f}")
    print(f"  Oxidizer Tank: {SM2.OxidizerTank:.3f}")
    print(f"  Propellant Tank: {SM2.PropellantTank:.3f}")
    print(f"  Oxidizer Tank Insulation: {SM2.OxidizerTankInsulation:.3f}")
    print(f"  Propellant Tank Insulation: {SM2.PropellantTankInsulation:.3f}")
    print(f"  Engine: {SM2.Engine:.3f}")
    print(f"  Thrust Structure: {SM2.ThrustStructure:.3f}")
    print(f"  Casing: {SM2.Casing:.3f}")
    print(f"  Gimbals: {SM2.Gimbals:.3f}")
    print(f"  Avionics: {SM2.Avionics:.3f}")
    print(f"  Wiring: {SM2.Wiring:.3f}")
    # Fairings (from M or M.rm if available)
    if hasattr(M, 'rm'):
        print("Fairings:")
        print(f"  Payload Fairing: {getattr(M.rm, 'PayloadFairing', float('nan')):.3f}")
        print(f"  Inter Tank Fairing: {getattr(M.rm, 'InterTankFairing', float('nan')):.3f}")
        print(f"  Inter Stage Fairing: {getattr(M.rm, 'InterStageFairing', float('nan')):.3f}")
        print(f"  Aft Fairing: {getattr(M.rm, 'AftFairing', float('nan')):.3f}")
    print(f"  Payload: {mPL:.3f}")

if __name__ == "__main__":
    LOX_LCH4  = Engine(3.6, 327, (2.26, 0.745), (2.4, 1.5), (35.16, 10.1), (34.34, 45), (1140,423),"LOX-LCH4")
    LOX_LH2   = Engine(6.03, 366, (1.86, 0.099), (2.4,2.15), (20.64, 4.2), (78, 84), (1140,71),"LOX-LH2")
    LOX_RP1   = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (1140,820),"LOX-RP1")
    SOLID     = Engine(1, 269, (4.5, 2.94), (6.6, 2.34), (10.5, 5), (16, 56), (0,1680),"SOLID")
    N2O4_UDMH = Engine(2.67, 285, (1.75, 0.067), (1.5, 1.13), (15.7, 14.7), (26.2, 81.3), (1442,781),"N2O4-UDMH")

    Submission2(LOX_LH2,LOX_LH2)