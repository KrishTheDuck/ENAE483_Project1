import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

#first stage delta V fraction vs mass

class Solver:
  def __init__(self, RocketCase):
    self.Rocket = RocketCase
    self.X = np.linspace(0.01,0.99,1500) #1%->99% with 1% intervals for the X split

  def MinimumMass(self):
  #Finds the minimum mass solution and returns the X split value and the mass(es), additionally it creates a pretty plot
    X,m0s,StageMasses = self.Rocket.MassTrends(self.X)
    minIndex = np.nanargmin(m0s)
    m0s = [m / 1000 for m in m0s]
    fig,ax = plt.subplots(figsize=(10,6))
    ax.plot(X,m0s,label="m0")
    # show minimum with 3 significant figures
    ax.plot(X[minIndex],m0s[minIndex],'ro',label=f"Minimum mass: {m0s[minIndex]:.3g} metric tons",markersize=12)
    ax.grid(True)
    ax.set_xlabel("dV Fraction")
    ax.set_ylabel("m0 (Wet mass) Metric Tonnes")
    ax.set_title("m0 vs dV Fraction -- S1: %s, S2: %s" %(self.Rocket.engines[0].Name,self.Rocket.engines[1].Name))
    ax.legend()

    # format axis tick labels to 3 significant figures
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3g}'))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3g}'))

    return X[minIndex],m0s[minIndex],(StageMasses[0][minIndex],StageMasses[1][minIndex]),fig

  def MinimumCost(self):
    #finds the minimum cost solution and returns the X split value and the cost, additionally it creates a pretty plot
    X,Costs = self.Rocket.CostTrends(self.X)
    minIndex = np.nanargmin(Costs["Total"])
    m1,m2 = self.Rocket.findMasses(X[minIndex]) #gets masses at minimum. prolly useful

    # extract costs at the minimum index and format for legend
    total_min = Costs["Total"][minIndex]
    s1_min = Costs["S1"][minIndex]
    s2_min = Costs["S2"][minIndex]

    # convert lists to numpy arrays before scaling
    total_arr = np.array(Costs["Total"]) / 1000
    s1_arr = np.array(Costs["S1"]) / 1000
    s2_arr = np.array(Costs["S2"]) / 1000

    fig,ax = plt.subplots(figsize=(10,6))
    # include min values (3 sig figs) in the legend labels
    ax.plot(X, total_arr, label=f"Total Cost (min {total_min/1000:.3g} B)")
    ax.plot(X, s1_arr, label=f"Stage 1 Cost ({s1_min/1000:.3g} B)")
    ax.plot(X, s2_arr, label=f"Stage 2 Cost ({s2_min/1000:.3g} B)")
    # label the vertical line with 3 significant figures for the cost value
    ax.axvline(X[minIndex], color='r', linestyle='--', linewidth=2,label=f"Minimum cost: ${total_min/1000:.3g}B")
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("dV Fraction")
    ax.set_ylabel("Cost $B")
    ax.set_title("Cost vs dV Fraction -- S1: %s, S2: %s" %(self.Rocket.engines[0].Name,self.Rocket.engines[1].Name))

    # format axis tick labels to 3 significant figures
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3g}'))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3g}'))

    return X[minIndex],(Costs["Total"][minIndex],Costs["S1"][minIndex],Costs["S2"][minIndex]) ,(m1,m2),fig
