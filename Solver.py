import matplotlib.pyplot as plt
import numpy as np

#first stage delta V fraction vs mass

class Solver:
  def __init__(self, RocketCase):
    self.Rocket = RocketCase
    self.X = np.linspace(0.01,0.99,98) #1%->99% with 1% intervals for the X split

  def MinimumMass(self):
  #Finds the minimum mass solution and returns the X split value and the mass(es), additionally it creates a pretty plot
    X,m0s,StageMasses = self.Rocket.MassTrends(self.X)
    minIndex = np.nanargmin(m0s)
    m0s = [m / 1000 for m in m0s]
    fig,ax = plt.subplots(figsize=(10,6))
    ax.plot(X,m0s,label="m0")
    ax.plot(X[minIndex],m0s[minIndex],'ro',label="Minimum mass",markersize=12)
    ax.grid(True)
    ax.set_xlabel("dV Fraction")
    ax.set_ylabel("m0 (Wet mass) Metric Tonnes")
    ax.set_title("m0 vs dV Fraction -- %s, %s" %(self.Rocket.engines[0].Name,self.Rocket.engines[1].Name))
    ax.legend()

    return X[minIndex],m0s[minIndex],(StageMasses[0][minIndex],StageMasses[1][minIndex]),fig

  def MinimumCost(self):
    #finds the minimum cost solution and returns the X split value and the cost, additionally it creates a pretty plot
    X,Costs = self.Rocket.CostTrends(self.X)
    minIndex = np.nanargmin(Costs["Total"])
    m1,m2 = self.Rocket.findMasses(X[minIndex]) #gets masses at minimum. prolly useful

    fig,ax = plt.subplots(figsize=(10,6))
    # self.__Plot(ax,X,Costs,POI=(X[minIndex],Costs[minIndex]),POI_name="Minimum Cost Point")
    ax.plot(X,Costs["Total"],label="Total Cost")
    ax.plot(X,Costs["S1"],label="Stage 1 Cost")
    ax.plot(X,Costs["S2"],label="Stage 2 Cost")
    ax.axvline(X[minIndex], color='r', linestyle='--', linewidth=2,label="Minimum cost")
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("dV Fraction")
    ax.set_ylabel("Cost $M")
    ax.set_title("Cost vs dV Fraction -- %s, %s" %(self.Rocket.engines[0].Name,self.Rocket.engines[1].Name))



    return X[minIndex],(Costs["Total"][minIndex],Costs["S1"][minIndex],Costs["S2"][minIndex]) ,(m1,m2),fig






