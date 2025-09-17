from Engine import Engine
from RocketCase import RocketCase
import matplotlib.pyplot as plt
import numpy as np
import Solver as S

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
    print(f"  dV fraction in Stage 1 (X): {X_mass:.3f}")
    print(f"  Overall LV mass: {m0_mass:.2f} metric tonnes")
    print(f"  LV Cost: {(R.findCost(St_mass[0]["m_in"])+R.findCost(St_mass[1]["m_in"]))/1000:.2f} B2025") #since delta1,2 are the same we can hack this to quickly return the inert mass
    print(f"Minimum Cost Solution:")
    print(f"  dV fraction in Stage 1 (X): {X_cost:.3f}")
    print(f"  Overall LV mass: {(m1_cost["m0"])/1000:.2f} metric tonnes")
    print(f"  Overall LV cost: ${Costs[0]/1000:.2f} B2025")
    print()

    plt.show()


if __name__ == "__main__":
    # Define available engines/propellant options
    LOX_LCH4  = Engine(3.6, 327, (2.26, 0.745), (2.4, 1.5), (35.16, 10.1), (34.34, 45), (1140,423),"Lox-LCH4")
    LOX_LH2   = Engine(6.03, 366, (1.86, 0.099), (2.4,2.15), (20.64, 4.2), (78, 84), (1140,71),"LOX-LH2")
    LOX_RP1   = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (1140,820),"LOX-RP1")
    SOLID     = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (0,1680),"SOLID")
    N2O4_UDMH = Engine(2.67, 285, (1.75, 0.067), (1.5, 1.13), (15.7, 14.7), (26.2, 81.3), (1442,781),"N2O4-UDMH")

    StageProps = [LOX_LCH4, LOX_LH2, LOX_RP1, SOLID, N2O4_UDMH]

    # Parameters used across cases
    dVtot = 12.3e3
    mPL = 26000
    delta1 = 0.08
    delta2 = 0.08

    # X grid to evaluate trends (matching Solver)
    # restrict dV fraction (Stage 1) search to 35% - 65%
    Xgrid = np.linspace(0.35,0.65,61)

    # helper to create compact labels for the legend to reduce clutter
    short_names = {
        "Lox-LCH4": "LCH4",
        "LOX-LH2":  "LH2",
        "LOX-RP1":  "RP1",
        "SOLID":    "SOLID",
        "N2O4-UDMH":"N2O4/UDMH"
    }
    def short(name):
        return short_names.get(name, name)

    # Collect results for plotting
    mass_curves = []   # list of (label, X, m0_metric_tonnes, s1_name, s2_name)
    cost_curves = []   # list of (label, X, total_cost_billions, s1_name, s2_name)

    # color mapping per 2nd-stage propellant (keeps consistent across plots)
    color_map = {
        "LCH4": "tab:blue",
        "LH2":  "tab:orange",
        "RP1":  "tab:green",
        "SOLID": "tab:red",
        "N2O4/UDMH": "tab:purple"
    }
    # linestyle mapping per 1st-stage propellant
    ls_map = {
        "LCH4": "-",
        "LH2":  "--",
        "RP1":  "-.",
        "SOLID": ":",
        "N2O4/UDMH": (0, (1, 1))
    }

    for s1 in StageProps:
        for s2 in StageProps:
            # use compact labels like "LCH4/LH2" to keep legend readable
            label = f"{short(s1.Name)}/{short(s2.Name)}"
            R = RocketCase(dVtot, mPL, (delta1, delta2), (s1, s2))

            # Mass trends (m0 in kg) -> convert to metric tonnes for plotting
            X_m, m0s, _ = R.MassTrends(Xgrid)
            m0s_tonnes = np.array(m0s) / 1000.0

            # Cost trends (Costs in millions) -> convert total to billions
            X_c, Costs = R.CostTrends(Xgrid)
            total_cost_b = np.array(Costs["Total"]) / 1000.0

            mass_curves.append((label, X_m, m0s_tonnes, short(s1.Name), short(s2.Name)))
            cost_curves.append((label, X_c, total_cost_b, short(s1.Name), short(s2.Name)))

    # Plot all mass curves on one figure
    fig_mass_all, axm = plt.subplots(figsize=(12, 8))
    for label, Xc, m0, s1n, s2n in mass_curves:
        clr = color_map.get(s2n, 'k')
        ls = ls_map.get(s1n, '-')
        axm.plot(Xc, m0, label=label, color=clr, linestyle=ls)
        # mark the minimum point if valid
        if not np.all(np.isnan(m0)):
            idx = np.nanargmin(m0)
            if not np.isnan(m0[idx]):
                axm.plot(Xc[idx], m0[idx], 'o')
                axm.text(Xc[idx], m0[idx], f" {m0[idx]:.1f}t", fontsize=8)

    axm.set_xlabel('dV Fraction (Stage 1)')
    axm.set_ylabel('m0 (Wet mass) Metric Tonnes')
    axm.set_title('All Minimum Mass Curves (m0 vs dV fraction) for 25 Propellant Combos')
    axm.grid(True)
    # limit y-axis to 0 - 30,000 metric tonnes per user request
    axm.set_ylim(0, 30000)
    # reduce legend clutter: smaller font and two columns
    # main legend (all curves)
    axm.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='x-small', ncol=2)
    # secondary compact legends: color = 2nd-stage, linestyle = 1st-stage
    from matplotlib.lines import Line2D
    color_handles = [Line2D([0], [0], color=color_map[name], lw=4, label=f'S2: {name}') for name in color_map]
    ls_handles = [Line2D([0], [0], color='k', linestyle=ls_map[name], lw=2, label=f'S1: {name}') for name in ls_map]
    # place the legends outside the plot area
    leg1 = axm.legend(handles=color_handles, loc='upper left', bbox_to_anchor=(1.02, 1.0), title='2nd-stage color', fontsize='small')
    axm.add_artist(leg1)
    axm.legend(handles=ls_handles, loc='lower left', bbox_to_anchor=(1.02, 0.3), title='1st-stage linestyle', fontsize='small')
    fig_mass_all.tight_layout()

    # Plot all total-cost curves on one figure
    fig_cost_all, axc = plt.subplots(figsize=(12, 8))
    for label, Xc, cost_b, s1n, s2n in cost_curves:
        clr = color_map.get(s2n, 'k')
        ls = ls_map.get(s1n, '-')
        axc.plot(Xc, cost_b, label=label, color=clr, linestyle=ls)
        # mark the minimum cost point if valid
        if not np.all(np.isnan(cost_b)):
            idx = np.nanargmin(cost_b)
            if not np.isnan(cost_b[idx]):
                axc.plot(Xc[idx], cost_b[idx], 'o')
                axc.text(Xc[idx], cost_b[idx], f" ${cost_b[idx]:.2f}B", fontsize=8)

    axc.set_xlabel('dV Fraction (Stage 1)')
    axc.set_ylabel('Total Cost ($B, 2025)')
    axc.set_title('All Total Cost Curves (Total Cost vs dV fraction) for 25 Propellant Combos')
    axc.grid(True)
    # limit y-axis to 0 - 50 billion dollars per user request
    axc.set_ylim(0, 50)
    # reduce legend clutter: smaller font and two columns
    axc.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='x-small', ncol=2)
    # add color and linestyle legends for the cost plot as well
    color_handles_c = [Line2D([0], [0], color=color_map[name], lw=4, label=f'S2: {name}') for name in color_map]
    ls_handles_c = [Line2D([0], [0], color='k', linestyle=ls_map[name], lw=2, label=f'S1: {name}') for name in ls_map]
    leg1c = axc.legend(handles=color_handles_c, loc='upper left', bbox_to_anchor=(1.02, 1.0), title='2nd-stage color', fontsize='small')
    axc.add_artist(leg1c)
    axc.legend(handles=ls_handles_c, loc='lower left', bbox_to_anchor=(1.02, 0.3), title='1st-stage linestyle', fontsize='small')
    fig_cost_all.tight_layout()

    # Show both figures
    plt.show()
