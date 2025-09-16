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
    X, m0, St, fig = Sol.MinimumMass()  # returns minimum mass solution (with plot)
    Xm,Costs,(m1,m2),fig = Sol.MinimumCost() #returns minimum cost solution (with plot)
    plt.show()


if __name__ == "__main__":
    LOX_LCH4  = Engine(3.6, 327, (2.26, 0.745), (2.4, 1.5), (35.16, 10.1), (34.34, 45), (1140,423),"Lox-LCH4")
    LOX_LH2   = Engine(6.03, 366, (1.86, 0.099), (2.4,2.15), (20.64, 4.2), (78, 84), (1140,71),"LOX-LH2")
    LOX_RP1   = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (1140,820),"LOX-RP1")
    SOLID     = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (0,1680),"SOLID")
    N2O4_UDMH = Engine(2.67, 285, (1.75, 0.067), (1.5, 1.13), (15.7, 14.7), (26.2, 81.3), (1442,781),"N204-UDMH (Storables)")



    #Example workflow for generating required plots for a Storable second stage
    Stage1Props = [LOX_LCH4,LOX_LH2,LOX_RP1,SOLID,N2O4_UDMH]
    Stage2Prop = N2O4_UDMH
    for i in Stage1Props:
        S2ndStage(i,Stage2Prop)
        #todo Solver function also provides stats for cost and mass plots however currently they are not being used. Modify this for the actual submission I reckon.




