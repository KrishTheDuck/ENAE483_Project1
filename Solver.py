import matplotlib.pyplot as plt
import numpy as np

# first stage delta V fraction vs mass


class Solver:
    def __init__(self, RocketCaseObject):
        self.RocketCaseObject = RocketCaseObject
        self.X, self.m0s, self.StageMasses = self.RocketCaseObject.MassTrends(
            np.linspace(0.35, 0.65, 61)
        )
        _, self.Costs = self.RocketCaseObject.CostTrends(self.X)

    def PlotMinimumMass(self):
        # Finds the minimum mass solution and returns the X split value and the mass(es), additionally it creates a pretty plot
        minIndex = np.nanargmin(self.m0s)
        m0s = [m / 1000 for m in self.m0s]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.X, m0s, label="m0")
        ax.plot(
            self.X[minIndex],
            m0s[minIndex],
            "ro",
            label="Minimum mass: %.2fkg" % (m0s[minIndex]),
            markersize=12,
        )
        ax.grid(True)
        ax.set_xlabel("dV Fraction")
        ax.set_ylabel("m0 (Wet mass) Metric Tonnes")
        ax.set_title(
            f"m0 vs dV Fraction -- S1: {self.RocketCaseObject.engines[0].Name}, S2: {self.RocketCaseObject.engines[1].Name}"
        )
        ax.legend()

        return (
            self.X[minIndex],
            m0s[minIndex],
            (self.StageMasses[0][minIndex], self.StageMasses[1][minIndex]),
            fig,
        )

    def PlotMinimumCost(self):
        # finds the minimum cost solution and returns the X split value and the cost, additionally it creates a pretty plot
        minIndex = np.nanargmin(self.Costs["Total"])
        m1, m2 = self.RocketCaseObject.findMasses(
            self.X[minIndex]
        )  # gets masses at minimum. prolly useful

        fig, ax = plt.subplots(figsize=(10, 6))
        # self.__Plot(ax,X,Costs,POI=(X[minIndex],Costs[minIndex]),POI_name="Minimum Cost Point")
        ax.plot(self.X, self.Costs["Total"], label="Total Cost")
        ax.plot(self.X, self.Costs["S1"], label="Stage 1 Cost")
        ax.plot(self.X, self.Costs["S2"], label="Stage 2 Cost")
        ax.axvline(
            self.X[minIndex],
            color="r",
            linestyle="--",
            linewidth=2,
            label=f"Minimum cost: ${self.Costs['Total'][minIndex]:.2f}M",
        )
        ax.grid(True)
        ax.legend()
        ax.set_xlabel("dV Fraction")
        ax.set_ylabel("Cost $M")
        ax.set_title(
            f"Cost vs dV Fraction -- S1: {self.RocketCaseObject.engines[0].Name}, S2: {self.RocketCaseObject.engines[1].Name}"
        )

        return (
            self.X[minIndex],
            (
                self.Costs["Total"][minIndex],
                self.Costs["S1"][minIndex],
                self.Costs["S2"][minIndex],
            ),
            (m1, m2),
            fig,
        )
