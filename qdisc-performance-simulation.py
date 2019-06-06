import numpy as np
import math

simulationDuration = 100
minFeatureDuration = 1
maxFeatureDuration = 20
minValue = 0
maxValue = 10000
numRuns = 1000

results = []

i = 0
while i < numRuns:
    features = []

    x = 0
    while x < 10:
        features.append(np.random.randint(minFeatureDuration, maxFeatureDuration+1))
        x += 1

    elapsedWeeks = 0
    accruedValue = 0
    numDeliveredFeatures = 0
    while elapsedWeeks < simulationDuration:
        currentFeatureDuration = features.pop(np.random.randint(0, len(features)))
        if (elapsedWeeks+currentFeatureDuration) > simulationDuration:
            break

        numberNewFeatures = math.floor((elapsedWeeks+currentFeatureDuration)/2) - math.floor(elapsedWeeks/2)
        while numberNewFeatures > 0:
            features.append(np.random.randint(minFeatureDuration, maxFeatureDuration+1))
            numberNewFeatures -= 1

        elapsedWeeks += currentFeatureDuration
        accruedValue += np.random.randint(minValue, maxValue+1)
#         accruedValue += (simulationDuration - elapsedWeeks) * np.random.randint(minValue, maxValue+1)
        numDeliveredFeatures +=1

    results.append(accruedValue)
    print("Total Features: %d; Delivered Feautres %d" % (numDeliveredFeatures + len(features), numDeliveredFeatures))
    i += 1

print("Random Prioritization, No Right Sizing", np.percentile(results,[10,20,30,40,50,60,70,80,90]))