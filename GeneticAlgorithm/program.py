import random
#import itertools
import numpy as np
import time
import csv
import pandas as pd
#import concurrent.futures
#import plotly.express as px
import math

truck_capacities=[320,250,200]
truck_costs=[7900,6300,480]


def divide_chunks(l, n):
    """
    Yield successive n-sized
    chunks from l.
    Taken from: https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
    """    
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def getFitness(strategy, cleaningSessions):
    fitness = 0
    trucks_strategy = list(divide_chunks(strategy, 15))
    for sesion in range(cleaningSessions):
        buildings = {n:[0,0] for n in range(sesion)}
        truck_capacities=[320,250,200]
        truck_costs=[7900,6300,480]
        truck_uses=[0]*3
        for weekday in range(1,8):
            for building in buildings.keys():
                buildings[building][0]=buildings[building][0]+ random.randint(0, 15)
                buildings[building][1]=buildings[building][1]+ random.randint(0, 15)
            for truck_strategy,truck in zip(trucks_strategy,list(range(0,2))):
                pick_day,pick_night = truck_strategy[2*weekday-1],truck_strategy[2*weekday]
                if(truck_strategy[0] == 0): #non biological risk
                    for building in buildings.keys():
                        if(pick_day == 1): 
                            truck_capacities[truck] = truck_capacities[truck] - buildings[building][0]
                            buildings[building][0]=0
                            truck_uses[truck]+=1
                            if(truck_capacities[truck] < 0):
                                return -1e9
                        elif(pick_night == 1):
                            truck_capacities[truck] = truck_capacities[truck] - buildings[building][0]
                            buildings[building][0]=0
                            truck_uses[truck]+=1
                            if(truck_capacities[truck] < 0):
                                return -1e9
                else: #biological risk
                    for building in buildings.keys():
                        if(pick_night == 1 or weekday==5 or weekday==6):
                            truck_capacities[truck] = truck_capacities[truck] - buildings[building][1]
                            buildings[building][1]=0
                            truck_uses[truck]+=1
                            if(truck_capacities[truck] < 0):
                                return -1e9
        if (sum([v[0]+v[1] for v in buildings.values()])<30):
            fitness+=2e6
        cost_function = sum([cost*use for cost,use in zip(truck_costs,truck_uses)])
        fitness-=cost_function   
    fitness /= cleaningSessions
    return fitness



def tryAllStrategies(strategies, population, cleaningSessions):
    population = []
    for strategy in strategies:
        fitness = getFitness(strategy, cleaningSessions)
        population.append((strategy, fitness))
    return population


def defaultMutation(children):
    for i in range(len(children)):
        if(random.random() < 0.01):  # Mutation
            children[i][random.randint(0, len(children[i])-1)] = random.randint(0, 1)
    return children
def swapMutation(children):
    for child in children:
        if (random.random()<0.2):
            indexToChange=(random.randint(0,len(child)-1),random.randint(0,len(child)-1))
            child[indexToChange[0]],child[indexToChange[1]]=child[indexToChange[1]],child[indexToChange[0]]
    return children
def newDefaultMutation(children):
    for i in range(len(children)):
        for j in range(len(children[i])):
            if(random.random()<0.05): # Mutation
                children[i][j]=random.randint(0,6)
    return children
def inversion(children):
    for child in children:
        if (random.random()<0.05):
            value=random.randint(1,len(child)//2)
            interval=(value,value+random.randint(0,len(child)//2))
            child[interval[0]:interval[1]]=child[interval[1]-1:interval[0]-1:-1]
    return children

def generateStrategies(n, length):
    strategies = []
    for strategy in range(n):
        randomlist = [random.randint(0, 1) for _ in range(length)]
        strategies.append(randomlist)
    return strategies


def mate(father, mother, mutationFunction=defaultMutation):
    genXY, genXX = father, mother
    num = random.randint(0, len(father)-1)
    children = [
        genXY[:num]+genXX[num:],
        genXX[:num]+genXY[num:]
    ]
    children = mutationFunction(children)
    return children


def defaultNewPopulation(newStrategies, lengthPopulation, probabilities, population, mutationFunction, mate=mate):
    while(len(newStrategies) < 200):
        parents = np.random.choice(lengthPopulation, 2, p=probabilities)
        father, mother = population[parents[0]], population[parents[1]]
        children = mate(father[0], mother[0], mutationFunction)
        newStrategies.append(children[0])
        newStrategies.append(children[1])
    return newStrategies


def getProbabilities(fitnessValues):
    maxValue = max(fitnessValues)
    minValue = min(fitnessValues)
    normalized = list(
        map(
            lambda x: (x - minValue) / (maxValue - minValue),
            fitnessValues
        )
    )
    total = sum(normalized)
    probabilities = list(map(lambda x: x/total, normalized))
    probabilities.sort(reverse=True)
    return probabilities


def run(f, sizeGene, mutationFunction=defaultMutation, generateNewPopulation=defaultNewPopulation, mate=mate, getProbabilities=getProbabilities):
    """
    Main function
    It considers the following aspects to execute the genetic algorithm:
    A chromosome of 45 elements divided into 3 segments that represent the 
    information on the use of each truck: the first element represents the type of truck 
    (if it collects biohazardous waste or non-hazardous waste). 

    The other 14 represent whether the truck passes during business hours or not on each 
    day of the week: that is, the first two digits represent whether the truck passes 
    during the day or at night on Monday, the next two on Tuesday, then Wednesday, 
    Thursday and so on until Sunday.

    """
    writer = csv.writer(f)
    writer.writerow(["generation", "gene", "fitness"])
    timeStart = time.time()
    cleaningSessions = 10
    firstStrategies = generateStrategies(200, sizeGene)
    print(f"""University Garbage Collector
    
    With size gene of {sizeGene} \n""")
    strategies = firstStrategies
    maxFitness = []
    population = []
    for generation in range(500):
        print("Starting generation ", generation)
        population = tryAllStrategies(strategies, population, cleaningSessions)
        population.sort(reverse=True, key=lambda y: y[1])
        maxFitness.append(population[0][1])  # for painting
        writer.writerow([generation, population[0][0], population[0][1]])
        newStrategies = []
        lengthPopulation = len(population)
        fitnessValues = [population[i][1] for i in range(lengthPopulation)]
        probabilities = getProbabilities(fitnessValues)
        strategies = generateNewPopulation(
            newStrategies, lengthPopulation, probabilities, population, mutationFunction, mate)
        population = []
        print("Generation", generation, "=", maxFitness[generation])
        print("Execution time: ", round(time.time() - timeStart, 4), "seconds")
    f.close()





def plotFitnes(fitnesScore):
    generation = [fitnesScore.index(n) + 1 for n in fitnesScore]

    df = pd.DataFrame(dict(
        Generation=generation,
        y=fitnesScore
    ))
    fig = px.line(df, x="Generation", y="y", title="Fitness vs Generation", markers=True,
                  labels={
                      "y": "Best fitness in population"
                  })
    fig.show()
    plotFitnes(fitnesScore)

def multipleCrossover(father,mother,mutationFunction=defaultMutation):
    genY,genX = father,mother
    nOfslices=random.randint(2,2*int(math.sqrt(len(father))))
    genYWithSlices = list(divide_chunks(genY,nOfslices))
    genXWithSlices = list(divide_chunks(genX,nOfslices))
    children=[[],[]]
    for i in range(len(genXWithSlices)):
        if i%2==0:
            children[0]+=genXWithSlices[i]
            children[1]+=genYWithSlices[i]
        else:
            children[0]+=genYWithSlices[i]
            children[1]+=genXWithSlices[i]
    children=mutationFunction(children)
    return children
if __name__ == '__main__':
    f = open("generationData.csv", "w")
    run(f, 45,mate=multipleCrossover,mutationFunction=inversion)
