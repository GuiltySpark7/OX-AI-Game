import oxGameClassified as oxGame
import oxAI
import numpy as np
import pandas as pd
import pickle

def load_topOPlayers():
    with open("OAIdump", "rb") as input:
        print("loading Oplayers")
        topOPlayersLoaded = pickle.load(input)
    return topOPlayersLoaded


def load_topXPlayers():
    with open("XAIdump", "rb") as input:
        print("loading Xplayers")
        topXPlayersLoaded = pickle.load(input)
    return topXPlayersLoaded


topOPlayersLoaded = load_topOPlayers()
topXPlayersLoaded = load_topXPlayers()
Oplayers = pd.DataFrame(topOPlayersLoaded)
Xplayers = pd.DataFrame(topXPlayersLoaded)
topOPlayersLoaded
topXPlayersLoaded
topXPlayersLoaded
player = Oplayers.loc[Oplayers['score'].argmax()]
playerSeed = player['AI']


def genVarFromSeed(playerSeed, variations, weightsNoise=0.2, biasNoise=0.1):
    players = []
    for i in np.arange(0, variations):
        players.append({"AI": oxAI.AI([9, 15, 12, 9]), "score": 0})

    for j in players:
        # calc variations
        newWeights = []
        for i in playerSeed.weights:
            weights = i.flatten()
            weights = weights + np.random.uniform(low=-weightsNoise,
                                                  high=weightsNoise,
                                                  size=len(weights))
            weights = np.reshape(weights, np.shape(i))
            newWeights.append(weights)
        newBias = []
        for i in playerSeed.bias:
            bias = i
            bias = bias + np.random.uniform(low=-biasNoise,
                                            high=biasNoise,
                                            size=len(bias))
            newBias.append(bias)
        j['AI'].weights = newWeights
        j['AI'].bias = newBias
    return players

def gameOfGames(OPlayers, XPlayers):
    OPlayersPD = pd.DataFrame(OPlayers)
    XPlayersPD = pd.DataFrame(XPlayers)
    OPlayersPD['score'] = 0
    XPlayersPD['score'] = 0
    OPlayers = OPlayersPD.to_dict('records')
    XPlayers = XPlayersPD.to_dict('records')
    test = oxGame.oxGame(XPlayers[0], OPlayers[0], 3, 3, 1, 3)
    # every x player is matched against every O player and their scores recorded
    for j in np.arange(0, len(OPlayers)):
        if j % 10 == 0:
            print(j)
        else:
            print(j, end=" ")
        test.player0 = OPlayers[j]["AI"]
        test.PlayerXScore = 0
        test.Player0Score = 0
        for i in np.arange(0, len(XPlayers)):
            test.playerX = XPlayers[i]["AI"]
            OscoreOld = test.Player0Score
            test.runGame(0)
            if test.Player0Score == OscoreOld:
                XPlayers[i]["score"] += 1
        OPlayers[j]["score"] = len(XPlayers) - test.PlayerXScore
    return OPlayers, XPlayers


topPlayers = topXPlayersLoaded
topPlayers.extend(topOPlayersLoaded)
player = topXPlayersLoaded[90]
print(topPlayers)
groupOfInterest = OPlayers
analysis = pd.DataFrame(groupOfInterest)
analysis['score'].argmax()
player = groupOfInterest[analysis['score'].argmax()]
player
topXPlayersLoaded

players = genVarFromSeed(player['AI'], 200)
OPlayers, XPlayers = gameOfGames(players, topPlayers)
OPlayers, XPlayers = gameOfGames(OPlayers, XPlayers)
OPlayers
XPlayers

OPlayers, XPlayers = gameOfGames(topOPlayersLoaded, topXPlayersLoaded)
len(OPlayers)
XPlayers = pd.DataFrame(XPlayers)
XPlayers['score']

# human matchup code
def humanPlayer(game, winConnectLen):
    print(game)
    row = int(input("row"))
    col = int(input('column'))
    return row, col

playerX = playerSeed
playerO = humanPlayer

test = oxGame.oxGame(playerO, playerX, 3, 3, 1, 3)
test.runGame(0)
