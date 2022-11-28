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


def load_players(fileName):
    with open(fileName, "rb") as input:
        print("loading players " + fileName)
        playersLoaded = pickle.load(input)
    return playersLoaded


def save_topOPlayers(players):
    with open("topOPlayers", "wb") as output:
        pickle.dump(players, output, pickle.HIGHEST_PROTOCOL)


def save_topXPlayers(players):
    with open("topXplayers", "wb") as output:
        pickle.dump(players, output, pickle.HIGHEST_PROTOCOL)


def save_players(players, fileName):
    with open(fileName, "wb") as output:
        pickle.dump(players, output, pickle.HIGHEST_PROTOCOL)


# Generate Random AI
def genRandomAI(number, neurons=[9, 15, 12, 9]):
    OPlayers = []
    XPlayers = []
    # Creste Players. number of players to face off and neurons defined bellow
    for i in np.arange(0, number):
        OPlayers.append({"AI": oxAI.AI(neurons), "score": 0})
        XPlayers.append({"AI": oxAI.AI(neurons), "score": 0})
    return pd.DataFrame(OPlayers), pd.DataFrame(XPlayers)


# generates random variations of the playerseed AI. number of variations
# specified by "variations". how much to randomly fiddle the weights and bias
# values by is defined by the corisponding noise keywords
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
            weights = np.clip(weights, -5, 5)
            newWeights.append(weights)
        newBias = []
        for i in playerSeed.bias:
            bias = i
            bias = bias + np.random.uniform(low=-biasNoise,
                                            high=biasNoise,
                                            size=len(bias))
            bias = np.clip(bias, -2, 2)
            newBias.append(bias)

        j['AI'].weights = newWeights
        j['AI'].bias = newBias
    return pd.DataFrame(players)


def gameOfGames(OPlayers, XPlayers):
    OPlayers = pd.DataFrame(OPlayers)
    XPlayers = pd.DataFrame(XPlayers)
    OPlayers['score'] = 0
    XPlayers['score'] = 0

    test = oxGame.oxGame(XPlayers.loc[0], OPlayers.loc[0], 3, 3, 1, 3)
    # every xplayer is matched against every Oplayer and their scores recorded
    for j in np.arange(0, len(OPlayers)):
        test.player0 = OPlayers.loc[j, 'AI']
        test.PlayerXScore = 0
        test.Player0Score = 0
        for i in np.arange(0, len(XPlayers)):
            test.playerX = XPlayers.loc[i, 'AI']
            OscoreOld = test.Player0Score
            XscoreOld = test.PlayerXScore
            test.runGame(0)
            if test.Player0Score == OscoreOld + 1:
                XPlayers.loc[i, 'score'] -= 1
                OPlayers.loc[j, 'score'] += 1
            if test.PlayerXScore == XscoreOld + 1:
                XPlayers.loc[i, 'score'] += 1
                OPlayers.loc[j, 'score'] -= 1
        if j % 20 == 0:
            print(OPlayers.loc[j, 'score'])
        else:
            print(OPlayers.loc[j, 'score'], end=" ")
    return OPlayers, XPlayers


def AIBootcamp(rounds, squadSize):
    topOPlayers = []
    topXPlayers = []
    for K in np.arange(0, rounds):
        print(f"round {K}")
        OPlayers, XPlayers = genRandomAI(squadSize)
        OPlayers, XPlayers = gameOfGames(OPlayers, XPlayers)
        topOPlayers.append(OPlayers.loc[OPlayers['score'].argmax()])
        topXPlayers.append(XPlayers.loc[XPlayers['score'].argmax()])
    return pd.DataFrame(topOPlayers), pd.DataFrame(topXPlayers)


# human matchup code
def humanPlayer(game, winConnectLen):
    print(game)
    row = int(input("row"))
    col = int(input('column'))
    return row, col


def refinePlayers(refineList, combatants, batchSize=100, geneticDiversity=5, stagMax=5, refineXPlayers=False):
    varPerSeed = int(batchSize / geneticDiversity)
    refinedPlayers = pd.DataFrame(columns=['AI', 'score'])
    count = 0
    for playerSeed in refineList['AI']:
        topPlayer = pd.DataFrame([{'AI': playerSeed,
                                   'score': 0}])
        newPlayers = genVarFromSeed(playerSeed, batchSize)
        newPlayers = pd.concat([newPlayers, topPlayer]).reset_index(drop=True)
        newSeed = False
        highscoreOld = 0
        biasNoise = 0.1
        weightsNoise = 0.2
        stagnationCount = 0
        print("New Player!")
        print(playerSeed)
        count += 1
        print(count)
        while newSeed is False:
            # Play off all newPlayers against test set, score them, sort them by score
            if refineXPlayers is True:
                OPlayers, newPlayers = gameOfGames(combatants, newPlayers)
            else:
                newPlayers, XPlayers = gameOfGames(newPlayers, combatants)
            newPlayers = newPlayers.sort_values(by='score', ascending=False, ignore_index=True)

            # check on whether the evolution of players is progressing or stagnating
            # if it is stagnating, increase the variation of the player sets generated
            # if it seems stuck then move onto the next player in refineList
            highscoreNew = newPlayers.loc[0, 'score']
            if highscoreNew <= highscoreOld:
                stagnationCount = stagnationCount + 1
            else:
                stagnationCount = 0
                biasNoise = 0.1
                weightsNoise = 0.2
            if stagnationCount > 2:
                biasNoise = biasNoise * 1.5
                weightsNoise = weightsNoise * 1.5
            if stagnationCount > stagMax:
                # if stagnation detected then save best player to refinedPlayers,
                # reset and move onto next player in refine list
                newSeed = True
            highscoreOld = highscoreNew

            # Generate newPlayers for next round
            # take forward geneticDiversity best variations and use them to seed the next gen
            # of players. batchSize/geneticDiversity from each seed
            playerVariants = pd.DataFrame(columns=['AI', 'score'])
            playerSeeds = newPlayers.loc[0:geneticDiversity -1]
            for i in playerSeeds['AI']:
                playerVariants = pd.concat([playerVariants,
                                            genVarFromSeed(
                                            i, varPerSeed-1,
                                            weightsNoise=weightsNoise,
                                            biasNoise=biasNoise)]).reset_index(drop=True)

            newPlayers = pd.concat([playerSeeds, playerVariants]).reset_index(drop=True)
            print("HELLO")
            print(len(newPlayers))
            print(len(combatants))
            print(playerSeeds)
            print(f'stag Count: {stagnationCount}, weightsNoise: {weightsNoise}, biasNoise: {biasNoise}')

        # Save best Player from refning process before moving to next player
        topPlayer = pd.DataFrame([{'AI': newPlayers.loc[0, 'AI'],
                                   'score': newPlayers.loc[0, 'score']}])
        refinedPlayers = pd.concat([refinedPlayers, topPlayer]).reset_index(drop=True)

    return refinedPlayers
