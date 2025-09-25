from RocketCase import RocketCase

class MassRelations:
    def __init__(self,X,R: RocketCase):
        self.R = R
        self.X = X

        self.M1,self.M2 = self.R.findMasses(self.X)

        #Stage 1
        self.M1["m_ox"] = self.M1["m_pr"]*(self.R.engines[0].FMMR/(self.R.engines[0].FMMR+1)) #oxidizer mass
        self.M1["m_fu"] = self.M1["m_pr"]*(1/(self.R.engines[0].FMMR+1)) #fuel mass

        #Stage 2
        self.M2["m_ox"] = self.M2["m_pr"]*(self.R.engines[1].FMMR/(self.R.engines[1].FMMR+1)) #oxidizer mass
        self.M2["m_fu"] = self.M2["m_pr"]*(1/(self.R.engines[1].FMMR+1)) #fuel mass