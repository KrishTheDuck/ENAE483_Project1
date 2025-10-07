from Engine import Engine
from RocketCase import RocketCase
import matplotlib.pyplot as plt
import Solver as S
import MassRelations
from dataclasses import asdict
import numpy as np

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

def Submission2(Stage1,Stage2):
    #PARAMS
    dVtot = 12.3e3 #in m/s since all the rest of my calculations use base SI units
    mPL = 26000 #kg
    delta1 = 0.08
    delta2 = 0.08
    #More Params (we guess and check these bish)
    X = 0.55 #dV fraction in stage 1
    D_outer = 9 #m, outer diameter of the rocket

    R = RocketCase(dVtot,mPL,(delta1,delta2),(Stage1,Stage2))
    M = MassRelations.MassRelations(X,R,D_outer)
    
    SM1,SM2 = M.ReturnValues()

    print("\n--- Stage 1 Masses (SM1) ---")
    for attr, value in asdict(SM1).items():
        if isinstance(value, (int, float)) and not np.isnan(value):
            print(f"  {attr}: {value:.3g} kg")
        else:
            print(f"  {attr}: {value}")

    print("\n--- Stage 2 Masses (SM2) ---")
    for attr, value in asdict(SM2).items():
        if isinstance(value, (int, float)) and not np.isnan(value):
            print(f"  {attr}: {value:.3g} kg")
        else:
            print(f"  {attr}: {value}")

    print(SM1.DryMass/1e3,SM2.DryMass/1e3)

if __name__ == "__main__":
    LOX_LCH4  = Engine(3.6, 327, (2.26, 0.745), (2.4, 1.5), (35.16, 10.1), (34.34, 45), (1140,423),"LOX-LCH4")
    LOX_LH2   = Engine(6.03, 366, (1.86, 0.099), (2.4,2.15), (20.64, 4.2), (78, 84), (1140,71),"LOX-LH2")
    LOX_RP1   = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (1140,820),"LOX-RP1")
    SOLID     = Engine(1, 269, (4.5, 2.94), (6.6, 2.34), (10.5, 5), (16, 56), (0,1680),"SOLID")
    N2O4_UDMH = Engine(2.67, 285, (1.75, 0.067), (1.5, 1.13), (15.7, 14.7), (26.2, 81.3), (1442,781),"N2O4-UDMH")

    Submission2(LOX_LH2,LOX_LH2)