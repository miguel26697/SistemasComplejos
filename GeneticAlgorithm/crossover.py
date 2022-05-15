import random

from numpy import mat 
from program import divide_chunks,defaultMutation,run
import math



if __name__ == '__main__':
    f = open("generationData.csv", "w")
    run(f, 45,mate=multipleCrossover)