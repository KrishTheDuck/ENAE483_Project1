from Engine import Engine
from RocketCase import RocketCase
import matplotlib.pyplot as plt
import numpy as np
import Solver as S


def S2ndStage(Stage1Prop, Stage2Prop):
    # PARAMS
    dVtot = 12.3e3  # in m/s since all the rest of my calculations use base SI units
    mPL = 26000  # kg
    delta1 = 0.08
    delta2 = 0.08
    # SETUP
    R = RocketCase(dVtot, mPL, (delta1, delta2), (Stage1Prop, Stage2Prop))
    Sol = S.Solver(R)

    # SOlutions
    X_mass, m0_mass, St_mass, fig_mass = (
        Sol.PlotMinimumMass()
    )  # returns minimum mass solution (with plot)
    X_cost, Costs, (m1_cost, m2_cost), fig_cost = (
        Sol.PlotMinimumCost()
    )  # returns minimum cost solution (with plot)

    # Print summary for this propellant combo
    print(f"--- S1: {Stage1Prop.Name}, S2: {Stage2Prop.Name} ---")
    print(f"Minimum Mass Solution:")
    print(f"  dV fraction in Stage 1 (X): {X_mass:.3f}")
    print(f"  Overall LV mass: {m0_mass:.2f} metric tonnes")
    print(
        f"  LV Cost: {(R.findCost(St_mass[0]['m_in']) + R.findCost(St_mass[1]['m_in'])) / 1000:.2f} B2025"
    )
    print(f"Minimum Cost Solution:")
    print(f"  dV fraction in Stage 1 (X): {X_cost:.3f}")
    print(f"  Overall LV mass: {(m1_cost['m0'])/1000:.2f} metric tonnes")
    print(f"  Overall LV cost: ${Costs[0]/1000:.2f} B2025")
    print()

    plt.show()


if __name__ == "__main__":
    # Define available engines/propellant options
    LOX_LCH4 = Engine(
        3.6,
        327,
        (2.26, 0.745),
        (2.4, 1.5),
        (35.16, 10.1),
        (34.34, 45),
        (1140, 423),
        "Lox-LCH4",
    )
    LOX_LH2 = Engine(
        6.03,
        366,
        (1.86, 0.099),
        (2.4, 2.15),
        (20.64, 4.2),
        (78, 84),
        (1140, 71),
        "LOX-LH2",
    )
    LOX_RP1 = Engine(
        2.72,
        311,
        (1.92, 0.061),
        (3.7, 0.92),
        (25.8, 6.77),
        (37, 14.5),
        (1140, 820),
        "LOX-RP1",
    )
    SOLID = Engine(
        np.nan,
        269,
        (4.5, 2.94),
        (6.6, 2.34),
        (25.8, 6.77),
        (10.5, 5),
        (0, 1680),
        "SOLID",
    )
    N2O4_UDMH = Engine(
        2.67,
        285,
        (1.75, 0.067),
        (1.5, 1.13),
        (15.7, 14.7),
        (26.2, 81.3),
        (1442, 781),
        "N2O4-UDMH",
    )

    StageProps = [LOX_LCH4, LOX_LH2, LOX_RP1, SOLID, N2O4_UDMH]
    
    # Parameters used across cases
    dVtot = 12.3e3
    mPL = 26000
    delta1 = 0.08
    delta2 = 0.08

    # X grid to evaluate trends (matching Solver)
    # restrict dV fraction (Stage 1) search to 35% - 65%
    Xgrid = np.linspace(0.35, 0.65, 61)

    # helper to create compact labels for the legend to reduce clutter
    short_names = {
        "LOX-LCH4": "LCH4",
        "LOX-LH2": "LH2",
        "LOX-RP1": "RP1",
        "SOLID": "SOLID",
        "N2O4-UDMH": "N2O4/UDMH",
    }

    def short(name):
        return short_names.get(name, name)

    # Collect results for plotting
    mass_curves = []  # list of (label, X, m0_metric_tonnes, s1_name, s2_name)
    cost_curves = []  # list of (label, X, total_cost_billions, s1_name, s2_name)

    # color mapping per 2nd-stage propellant (keeps consistent across plots)
    color_map = {
        "LCH4": "tab:blue",
        "LH2": "tab:orange",
        "RP1": "tab:green",
        "SOLID": "tab:red",
        "N2O4/UDMH": "tab:purple",
    }
    # linestyle mapping per 1st-stage propellant
    ls_map = {
        "LCH4": "-",
        "LH2": "--",
        "RP1": "-.",
        "SOLID": ":",
        "N2O4/UDMH": (0, (1, 1)),
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
            cost_curves.append(
                (label, X_c, total_cost_b, short(s1.Name), short(s2.Name))
            )

    # Plot all mass curves on one figure
    # Create scatter-of-minima plot and connect minima for each first-stage propellant
    # Compute minima for each combo
    min_mass = {}  # s1n -> list of (s2n, Xmin, m0min)
    s2_order = [short(s.Name) for s in StageProps]
    for label, Xc, m0, s1n, s2n in mass_curves:
        if np.all(np.isnan(m0)):
            continue
        idx = int(np.nanargmin(m0))
        Xmin = float(Xc[idx])
        m0min = float(m0[idx])
        min_mass.setdefault(s1n, []).append((s2n, Xmin, m0min))

    # New: scatter minima colored by first-stage (common color per S1).
    # Use marker shape to distinguish 2nd-stage props and label each point with the combo.
    # define color per S1 and marker per S2
    color_map_s1 = {
        "LCH4": "tab:blue",
        "LH2": "tab:orange",
        "RP1": "tab:green",
        "SOLID": "tab:red",
        "N2O4/UDMH": "tab:purple",
    }
    marker_map_s2 = {
        "LCH4": "o",
        "LH2": "s",
        "RP1": "^",
        "SOLID": "D",
        "N2O4/UDMH": "v",
    }

    fig_mass_all, axm = plt.subplots(figsize=(12, 8))
    # plot each combo as a scatter point and connect minima for the same S1
    # sort and connect by X to form a function-like line (no back-and-forth)
    for s1n, pts in min_mass.items():
        # sort by X value (dV fraction) so the connecting line is monotonic in X
        pts_sorted = sorted(pts, key=lambda p: p[1])
        xs = [p[1] for p in pts_sorted]
        ys = [p[2] for p in pts_sorted]
        clr = color_map_s1.get(s1n, "k")
        # draw connecting line for this first-stage using its color
        axm.plot(xs, ys, color=clr, linestyle="-", linewidth=1, alpha=0.8)
        # draw scatter points and label each point with numeric m0 in tonnes
        for s2n, xval, yval in pts_sorted:
            mkr = marker_map_s2.get(s2n, "o")
            axm.scatter(xval, yval, color=clr, marker=mkr, edgecolor="k", s=120)
            # small x-offset for the text so it doesn't overlap the marker
            axm.text(xval + 0.002, yval, f"{yval:.1f}t", fontsize=8, va="center")

    axm.set_xlabel("dV Fraction (Stage 1)")
    axm.set_ylabel("m0 (Wet mass) Metric Tonnes")
    axm.set_title("Minima of m0 for each S1/S2 combo (points colored by S1)")
    axm.grid(True)
    axm.set_ylim(0, 30000)
    # separate legends: color = S1, marker = S2 (placed outside)
    from matplotlib.lines import Line2D

    color_handles = [
        Line2D([0], [0], color=color_map_s1[name], lw=6, label=f"{name}")
        for name in color_map_s1
    ]
    marker_handles = [
        Line2D(
            [0],
            [0],
            color="k",
            marker=marker_map_s2[name],
            linestyle="None",
            markersize=8,
            label=f"{name}",
        )
        for name in marker_map_s2
    ]
    leg_colors = axm.legend(
        handles=color_handles,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        title="S1 (color)",
        fontsize="small",
    )
    axm.add_artist(leg_colors)
    axm.legend(
        handles=marker_handles,
        loc="lower left",
        bbox_to_anchor=(1.02, 0.3),
        title="S2 (marker)",
        fontsize="small",
    )
    fig_mass_all.tight_layout()

    # Plot minima of total cost for each combo and connect minima by first-stage
    min_cost = {}  # s1n -> list of (s2n, Xmin, costmin)
    for label, Xc, cost_b, s1n, s2n in cost_curves:
        if np.all(np.isnan(cost_b)):
            continue
        idx = int(np.nanargmin(cost_b))
        Xmin = float(Xc[idx])
        cmin = float(cost_b[idx])
        min_cost.setdefault(s1n, []).append((s2n, Xmin, cmin))

    fig_cost_all, axc = plt.subplots(figsize=(12, 8))
    # plot each combo as a scatter point and connect minima for the same S1
    for s1n, pts in min_cost.items():
        pts_sorted = sorted(pts, key=lambda p: p[1])
        xs = [p[1] for p in pts_sorted]
        ys = [p[2] for p in pts_sorted]
        clr = color_map_s1.get(s1n, "k")
        # draw connecting line for this first-stage using its color
        axc.plot(xs, ys, color=clr, linestyle="-", linewidth=1, alpha=0.8)
        for s2n, xval, yval in pts_sorted:
            mkr = marker_map_s2.get(s2n, "o")
            axc.scatter(xval, yval, color=clr, marker=mkr, edgecolor="k", s=120)
            # label each marker with cost in billions (small x-offset)
            axc.text(xval + 0.002, yval, f"${yval:.2f}B", fontsize=8, va="center")

    axc.set_xlabel("dV Fraction (Stage 1)")
    axc.set_ylabel("Total Cost ($B, 2025)")
    axc.set_title("Minima of Total Cost for each S1/S2 combo (points colored by S1)")
    axc.grid(True)
    axc.set_ylim(0, 50)
    # separate legends: color = S1, marker = S2 (placed outside)
    color_handles_c = [
        Line2D([0], [0], color=color_map_s1[name], lw=6, label=f"{name}")
        for name in color_map_s1
    ]
    marker_handles_c = [
        Line2D(
            [0],
            [0],
            color="k",
            marker=marker_map_s2[name],
            linestyle="None",
            markersize=8,
            label=f"{name}",
        )
        for name in marker_map_s2
    ]
    leg_colors_c = axc.legend(
        handles=color_handles_c,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        title="S1 (color)",
        fontsize="small",
    )
    axc.add_artist(leg_colors_c)
    axc.legend(
        handles=marker_handles_c,
        loc="lower left",
        bbox_to_anchor=(1.02, 0.3),
        title="S2 (marker)",
        fontsize="small",
    )
    fig_cost_all.tight_layout()

    # Show both figures
    plt.show()
