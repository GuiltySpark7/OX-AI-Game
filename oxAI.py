import numpy as np


def sigmoid(A):
    return (1 / (1 + np.exp(-A)))

np.arange(1,4)

class AI:
    def __init__(self, neurons, weights=None, bias=None):
        self.neurons = neurons

        # autogenerate weights randomly
        if weights is None:
            weights = list()
            nextLayerInd = 1
            for i in neurons:
                if (nextLayerInd) < len(neurons):
                    weights.append(np.reshape(np.random.uniform(low=-5, high=5,
                    size=(i*neurons[nextLayerInd])), [neurons[nextLayerInd], i]))
                nextLayerInd += 1

        self.weights = weights

        if bias is None:
            bias = list()
            for i in np.arange(1, len(neurons)):
                bias.append(np.random.uniform(low=-1, high=1, size=neurons[i]))

        self.bias = bias

    def __call__(self,  game, winConnectionLen):
        layer = game.flatten()
        gameflat = layer
        for i in np.arange(0, len(self.weights)):
            layer = sigmoid(np.dot(self.weights[i], layer)) + self.bias[i]
        layer[gameflat != 2] = -100
        row = int(layer.argmax() / len(game[:,0]))
        col = (layer.argmax() - row * len(game[:,0]))
        return row, col

    def makeMove(self, game, winConnectionLen):
        layer = game.flatten()
        gameflat = layer
        for i in np.arange(0, len(self.weights)):
            layer = sigmoid(np.dot(self.weights[i], layer)) + self.bias[i]
        layer[gameflat != 2] = -100
        row = int(layer.argmax() / len(game[:,0]))
        col = (layer.argmax() - row * len(game[:,0]))
        return np.array([row, col])





"""

game = np.reshape(np.random.uniform(low=0, high=3, size=9).astype(int),[3,3])
game
game = game.flatten()
layer = np.array([0.1, 0.5, 0, 0.9, 0.95, 0, 0.98, 0.7, 0.8])
layer[game!=2] = 0
layer
layer.argmax()
a = 100
while a>0:
    testO = AI([9, 15, 12, 9])
    print(testO.makeMove(game,3))
    a = a-1

int(1.9)
game = np.random.uniform(low=0, high=3, size=9).astype(int)
np.around(test.calcOutput(game),1)

print(len(test.neurons))
print(len(test.weights))
a = list()
a
np.random.uniform(low=0, high=1, size=(neurons(ind)*neurons(ind+1)))
"""
