from Engine import Engine
import math
import numpy as np

class RocketCase:
    """
    """
    def __init__(self, dVtot : float, mPL : float, deltas : tuple[float,float], engines : tuple[Engine,Engine]):
      self.dVtot = dVtot
      self.mPL = mPL
      self.deltas = deltas
      self.engines = engines

    @property
    def gravity(self):
        return 9.81
    
    def findMasses(self, X):
      #Input: dV Fraction, total dV desired, Inert Mass Ratio
      #Returns two dictioaries for S1,S2 containing key-value pairs: m0,m_in,m_pr
      g = self.gravity #maybe use the @property here unsure
      # ISP1 = self.engines[0].Isp1 #doesnt work
      # ISP2 = self.engines[1].Isp2 #"
      ISP1 = self.engines[0].Isp
      ISP2 = self.engines[1].Isp

      dV1 = self.dVtot * X
      dV2 = self.dVtot * (1-X)

      #Stage 2 Calcs
      r2 = math.exp(-dV2/(g*ISP2))
      lambda2 = r2 - self.deltas[1]

      #Mass Calcs Stage 2
      m02 = self.mPL / (r2-self.deltas[1])
      m_in2 = m02*self.deltas[1]
      m_pr2 = m02 - self.mPL - m_in2

      Mass2 = {"m0":m02,
               "m_in":m_in2,
               "m_pr":m_pr2} #dict with stage 2 mass values
      #Stage 1 Calcs
      r1 = math.exp(-dV1/(g*ISP1))
      
      #Mass Calcs Stage 1
      m01 = m02 / (r1-self.deltas[0]) #we use m02 at the payload mass for stage 1
      m_in1 = m01*self.deltas[0]
      m_pr1 = m01 - m02 - m_in1
      Mass1 = {"m0":m01,
               "m_in":m_in1,
               "m_pr":m_pr1} #dict with stage 1 mass values
      return Mass1,Mass2

    def MassTrends(self, X):
      #Input: dV Fraction (linear iter), engines class (in particular the ISP's)
      #Returns XY array of dV and m0

      # #Assigment's
      # ISP1 = self.engines[0].Isp1 #I'm not sure how to engines class is defined but this is where I'd extract the useful parameters
      # ISP2 = self.engines[1].Isp2

      # pre-allocate as float array filled with NaN to avoid type warnings
      m0List = np.full(len(X), np.nan, dtype=float)
      S1List = []
      S2List = []
      for i, xi in enumerate(X):
        m1,m2 = self.findMasses(xi)
        S1List.append(m1)
        S2List.append(m2)

        # valid number check (because there is a "maximum" deltaV a stage can provide)
        try:
          if m1["m0"] > 0:
            m0List[i] = m1["m0"]
          else:
            m0List[i] = np.nan
        except Exception:
          m0List[i] = np.nan

      return X,m0List,(S1List,S2List)

    def CostTrends(self,X):
        #Input: dV Fraction (linear iter)
        #Returns XY array of dV and cost

        #Pre-allocating the costs as float arrays to allow np.nan
        Costs = {
            "S1": np.full(len(X), np.nan, dtype=float),
            "S2": np.full(len(X), np.nan, dtype=float),
            "Total": np.full(len(X), np.nan, dtype=float)
        }

        for i, xi in enumerate(X):
            #Finds Masses then calculats costs -- adding to dictionary
            m1, m2 = self.findMasses(xi)
            if m1["m0"] <= 0 or m2["m0"] <= 0:
                Costs["S1"][i] = np.nan
                Costs["S2"][i] = np.nan
                Costs["Total"][i] = np.nan
            else:
                Costs["S1"][i] = 13.52*m1["m_in"]**0.55
                Costs["S2"][i] = 13.52*m2["m_in"]**0.55
                Costs["Total"][i] = Costs["S1"][i] + Costs["S2"][i]

        return X, Costs

    def findCost(self,m_in):
        #Input: dV Fraction, Inert Mass
        #Returns cost of the rocket
        return 13.52*m_in**0.55
