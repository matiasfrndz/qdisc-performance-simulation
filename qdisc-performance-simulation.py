import numpy as np
import pandas as pd
import math
import random
import re

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

def calcPercentage(base, candidate):
    result = {
        "Queueing Discipline": "",
        "Value Reassessed": "",
        "Duration Reassessed": "",
        "Resized": ""
    }
    for k,v in candidate.items():
        if re.search("percentile", k):
            result[k] = '{:.0f}%'.format((v / base[k] - 1) * 100)

    return result

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

def runSimulationSet(title, set, out):
    simulationResults = []
    columns = ["Queueing Discipline", "Value Reassessed", "Duration Reassessed", "Resized", "10th percentile", "20th percentile", "30th percentile", "40th percentile", "50th percentile", "60th percentile", "70th percentile", "80th percentile", "90th percentile"]

    print(title)

    baseSim = set.pop(0);
    base = performSimulation(baseSim[0], reassessDuration=baseSim[1], reassessValue=baseSim[2], resize=baseSim[3])
    simulationResults.append(base)

    for sim in set:
        result = performSimulation(sim[0], reassessDuration=sim[1], reassessValue=sim[2], resize=sim[3])
        simulationResults.append(result)
        simulationResults.append(calcPercentage(base, result))

    df = pd.DataFrame(simulationResults, columns=columns)
    df.T.to_csv("out", sep="\t", header=False)
    print(df.T, "\n")


set = [
# Array format: qdisc, reassessDuration, reassessValue, resize
# see performSimulation
    [QDiscCD3(), False, False, False],
    [QDiscShortestJobFirst(), False, False, False],
    [QDiscRandom(), False, False, False]
]
runSimulationSet("Case I: CD3 Assumptions Are Met", set, "report-case-i.csv")

set = [
    [QDiscCD3(), False, True, False],
    [QDiscShortestJobFirst(), False, True, False],
    [QDiscRandom(), False, True, False]
]
runSimulationSet("Case II: CD3 Assumptions Not Met", set, "report-case-ii.csv")

set = [
    [QDiscCD3(), True, True, False],
    [QDiscShortestJobFirst(), True, True, False],
    [QDiscRandom(), True, True, False]
]
runSimulationSet("Case II: CD3 Assumptions Not Met (Version 2)", set, "report-case-ii_1.csv")

set = [
    [QDiscCD3(), False, True, True],
    [QDiscShortestJobFirst(), False, True, True],
    [QDiscRandom(), False, True, True]
]
runSimulationSet("Case III: Right Sizing of Items", set, "report-case-iii.csv")

