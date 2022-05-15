import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

f = open("generationData.csv","r",encoding="utf-8")
data = pd.read_csv(f)
f.close()
plt.plot(data['generation'],data['fitness'])
plt.show()