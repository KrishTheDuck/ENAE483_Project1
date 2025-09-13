from Engine import Engine
from RocketCase import RocketCase
import numpy as np
import Plotter as p

if __name__ == "__main__":
    LOX_LCH4  = Engine(3.6, 327, (2.26, 0.745), (2.4, 1.5), (35.16, 10.1), (34.34, 45), (1140,423))
    LOX_LH2   = Engine(6.03, 366, (1.86, 0.099), (2.4,2.15), (20.64, 4.2), (78, 84), (1140,71))
    LOX_RP1   = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (1140,820))
    SOLID     = Engine(2.72, 311, (1.92, 0.061), (3.7, 0.92), (25.8, 6.77), (37, 14.5), (0,1680))
    N2O4_UDMH = Engine(2.67, 285, (1.75, 0.067), (1.5, 1.13), (15.7, 14.7), (26.2, 81.3), (1442,781))
    
    #Example workflow using LOX-LCH4
    dVtot = 12.3e3 #in m/s since all the rest of my calculations use base SI units
    mPL = 26000 #kg
    delta1 = 0.08
    delta2 = 0.08
    Xsplit = np.linspace(0.01,0.99,98) #1%->99% with 1% intervals for the X split

    R = RocketCase(dVtot,mPL,(delta1,delta2),(LOX_LCH4,N2O4_UDMH))
    R.findMasses(0.5) #important X here is a FLOAT BETWEEN 0-1 AN ITERATABLE TYPE WILL THROW AN ERROR

    X,Y,_ = R.MassTrends(Xsplit)
    p.first_stage_delta_V_vs_mass(X,Y) #not sure this is correct. for starters we create a negative mass
