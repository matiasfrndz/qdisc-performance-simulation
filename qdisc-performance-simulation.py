import numpy as np
import pandas as pd
import math
import random

simulationDuration = 100
minFeatureDuration = 1
maxFeatureDuration = 20
minFeatureValue = 0
maxFeatureValue = 10000
maxDuration = 5
numRuns = 1000

class QDisc:
    def sort(self, anArray):
        return anArray

    def name(self):
        return "NoOp"

class QDiscRandom(QDisc):
    def sort(self, anArray):
        random.shuffle(anArray)
        return anArray

    def name(self):
        return "Random"

class QDiscCD3(QDisc):
    def sort(self, anArray):
        anArray.sort(key=lambda feature: feature['cd3value'], reverse=True)
        return anArray

    def name(self):
        return "CD3"

class QDiscShortestJobFirst(QDisc):
    def sort(self, anArray):
        anArray.sort(key=lambda feature: feature['estimatedDuration'], reverse=False)
        return anArray

    def name(self):
        return "Shortest First"

def generateRandomFeatureDuration():
    return np.random.randint(minFeatureDuration, maxFeatureDuration+1)

def generateRandomFeatureValue():
    return np.random.randint(minFeatureValue, maxFeatureValue+1)

def createFeature():
    estimatedDuration = generateRandomFeatureDuration()
    estimatedValue = generateRandomFeatureValue()
    cd3value = estimatedValue / estimatedDuration
    return {'estimatedDuration': estimatedDuration, 'estimatedValue': estimatedValue, 'cd3value': cd3value }

def performSimulation(qdisc, reassessDuration=False, reassessValue=True, resize=False):
    results = []

    i = 0
    while i < numRuns:
        features = []

        x = 0
        while x < 10:
            features.append(createFeature())
            x += 1

        elapsedWeeks = 0
        accruedValue = 0
        numDeliveredFeatures = 0
        while elapsedWeeks < simulationDuration:
            features = qdisc.sort(features)
            currentFeature = features.pop(0)

            if reassessDuration:
                currentFeatureDuration = generateRandomFeatureDuration()
            else:
                currentFeatureDuration = currentFeature['estimatedDuration']

            if resize and currentFeatureDuration > maxDuration:
                currentFeatureDuration = 5
                for x in range(3):
                    features.append(createFeature())

            if reassessValue:
                currentFeatureValue = generateRandomFeatureValue()
            else:
                currentFeatureValue = currentFeature['estimatedValue']

            if (elapsedWeeks+currentFeatureDuration) > simulationDuration:
                break

            numberNewFeatures = math.floor((elapsedWeeks+currentFeatureDuration)/2) - math.floor(elapsedWeeks/2)
            while numberNewFeatures > 0:
                features.append(createFeature())
                numberNewFeatures -= 1

            elapsedWeeks += currentFeatureDuration
            accruedValue += currentFeatureValue

        results.append(accruedValue)
        i += 1

    result = {
        "Queueing Discipline": qdisc.name(),
        "Value Reassessed": reassessValue,
        "Duration Reassessed": reassessDuration,
        "Resized": resize
    }
    i = 1
    for percentile in np.percentile(results,[10,20,30,40,50,60,70,80,90]):
        key = "%i0th percentile" % i
        result[key] = percentile
        i += 1
    return result

columns = ["Queueing Discipline", "Value Reassessed", "Duration Reassessed", "Resized", "10th percentile", "20th percentile", "30th percentile", "40th percentile", "50th percentile", "60th percentile", "70th percentile", "80th percentile", "90th percentile"]

simulationResults = []
simulationResults.append(performSimulation(QDiscCD3(), reassessDuration=False, reassessValue=False, resize=False))
simulationResults.append(performSimulation(QDiscShortestJobFirst(), reassessDuration=False, reassessValue=False, resize=False))
simulationResults.append(performSimulation(QDiscRandom(), reassessDuration=False, reassessValue=False, resize=False))

df = pd.DataFrame(simulationResults, columns=columns)
df.T.to_csv("report1.csv", sep="\t", header=False)
print(df.T, "\n")

simulationResults = []
simulationResults.append(performSimulation(QDiscCD3(), reassessDuration=False, reassessValue=True, resize=False))
simulationResults.append(performSimulation(QDiscShortestJobFirst(), reassessDuration=False, reassessValue=True, resize=False))
simulationResults.append(performSimulation(QDiscRandom(), reassessDuration=False, reassessValue=True, resize=False))

df = pd.DataFrame(simulationResults, columns=columns)
df.T.to_csv("report2.csv", sep="\t", header=False)
print(df.T, "\n")

simulationResults = []
simulationResults.append(performSimulation(QDiscCD3(), reassessDuration=False, reassessValue=True, resize=True))
simulationResults.append(performSimulation(QDiscShortestJobFirst(), reassessDuration=False, reassessValue=True, resize=True))
simulationResults.append(performSimulation(QDiscRandom(), reassessDuration=False, reassessValue=True, resize=True))

df = pd.DataFrame(simulationResults, columns=columns)
df.T.to_csv("report3.csv", sep="\t", header=False)
print(df.T, "\n")