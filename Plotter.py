import matplotlib.pyplot as plt
import numpy as np

#first stage delta V fraction vs mass
def first_stage_delta_V_vs_mass(Xfrac, mass0): #add Mika code vals as parameters

  #Not neccecarry we are already passing arrays as the parameters
  # # 2. Prepare your data (you can use simple Python lists or NumPy arrays)
  # x_coordinates = np.array(first_stage_delta_V)
  # y_coordinates = np.array(mass)

  # 3. Create the plot using plt.plot()
  plt.plot(Xfrac, mass0)

  # 4. (Recommended) Add labels and a title for clarity
  plt.xlabel("dV Fraction")
  plt.ylabel("m0 (Wet mass) Kg")
  plt.title("sample title")
  plt.grid(True) # Adds a grid to the background

  # 5. Display the plot
  plt.show()