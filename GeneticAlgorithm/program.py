import random
import itertools
import numpy as np
import time
import csv
import pandas as pd
import concurrent.futures
import plotly.express as px

truck_capacities=[320,250,200]
truck_costs=[7900,6300,480]
def getFitnessFromNumberOfSesions(strategy, numberOfSessions, numberOfActions, perceptions):
    fitness = 0
    N = 10
    for sesion in range(numberOfSessions):
        position = list(start)
        board = generateBoard(N)
        for iteration in range(numberOfActions):
            actualPerception = [getNorth(position, board, N),
                                getSouth(position, board, N),
                                getWest(position, board, N),
                                getEast(position, board, N),
                                getCurrent(position, board, N)
                                ]
            status = perceptions.index(actualPerception)
            action = strategy[status]
            fitness, board, position = applyAction(
                action, fitness, board, position, N)
    return fitness

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
    fitness = 1e6
    trucks_strategy = list(divide_chunks(strategy, 3))
    for sesion in range(cleaningSessions):
        buildings = {n:[0,0] for n in range(sesion)}
        truck_capacities=[320,250,200]
        truck_costs=[7900,6300,480]
        for weekday in range(7):
            for building in buildings.keys():
                buildings[building][0]=buildings[building][0]+ random.randint(0, 30)
                buildings[building][1]=buildings[building][1]+ random.randint(0, 30)
            for truck_strategy in trucks_strategy:
                if(truck_strategy[0] == 0): #non biological risk 
                    truck_capacities[0] = truck_capacities[0] - buildings[0][0]
                else: #biological risk
                    truck_capacities[0] = truck_capacities[0] - buildings[0][1]

    
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


def generateStrategies(n, length):
    strategies = []
    for strategy in range(n):
        randomlist = [random.randint(0, 1) for _ in range(length)]
        strategies.append(randomlist)
    return strategies


def generateBoard(N):
    board = []
    def putCan(): return int(random.random() > 0.5)
    for i in range(N):
        line = [putCan() for j in range(N)]
        board.append(line)
    return board


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
        population = tryAllStrategies(
            strategies, population, cleaningSessions)
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


def applyAction(action, fitness, board, position, N):
    if action == 0:
        newPos = (position[0], position[1]-1)
        if(newPos[1] < 0):
            fitness -= 5
            newPos = position
    elif action == 1:
        newPos = (position[0], position[1]+1)
        if(newPos[1] > N-1):
            fitness -= 5
            newPos = position
    elif action == 2:
        newPos = (position[0]-1, position[1])
        if(newPos[0] < 0):
            fitness -= 5
            newPos = position
    elif action == 3:
        newPos = (position[0]+1, position[1])
        if(newPos[0] > N-1):
            fitness -= 5
            newPos = position
    elif action == 4:
        newPos = position
    elif action == 5:
        newPos = position
        if(board[position[0]][position[1]]):
            fitness += 10
            board[position[0]][position[1]] = 0
        else:
            fitness -= 1
    elif action == 6:
        randAction = random.randint(0, 3)
        return applyAction(randAction, fitness, board, position, N)
    return (fitness, board, newPos)


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


if __name__ == '__main__':
    f = open("generationData.csv", "w")
    run(f, 45)
