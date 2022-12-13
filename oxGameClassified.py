import numpy as np


def player1(game, winConnectLen):
    print(game)
    return np.random.randint(len(game[:,0])), np.random.randint(len(game[0,:]))


def player2(game, winConnectLen):
    return np.random.randint(len(game[:,0])), np.random.randint(len(game[0,:]))


class oxGame:
    # instance attributes
    def __init__(self, playerX, player0, Rows, Cols, Games, winConnectLen):
        self.Rows = Rows
        self.Cols = Cols
        self.games = np.empty((Games, Rows, Cols), dtype=int)
        self.games[:] = 2
        self.maxTurns = Rows * Cols
        self.winConnectLen = winConnectLen

        self.playerX = playerX
        self.player0 = player0

        self.PlayerXScore = 0
        self.Player0Score = 0

        searchVectors = np.array([(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)])
        searchMask = np.zeros((4,(winConnectLen * 2) + 1,2), dtype=int)
        for i in np.arange(-winConnectLen, winConnectLen + 1):
            searchMask[:,winConnectLen - i] = searchVectors[0:4] * i
        self.searchMask = searchMask
        #print(searchMask)
        self.searchVectors = searchVectors

    # instance methods
    def runGame(self, gameNo):
        # set up game to be played
        self.games[gameNo] = 2
        game = self.games[gameNo]
        winConnectLen = self.winConnectLen
        turn = 1
        crosses = True
        gameOn = True

        # loop through taking turns until game is won or drawn
        while gameOn is True:
            # get input from correct player for empty slot, store in "move"
            if crosses is True:
                player = self.playerX
            else:
                player = self.player0
            inputEval = False
            while inputEval is False:
                # request move
                move = player(game, winConnectLen)
                # check if empty, if not request again
                if game[move] == 2:
                    game[move] = crosses
                    crosses = not crosses
                    turn += 1
                    inputEval = True


            # Check win Conditions
            if self.checkConnections(move, game) >= winConnectLen:
                # print(game)
                if not crosses is True:
                    winner = "X"
                    self.PlayerXScore += 1
                else:
                    winner = "0"
                    self.Player0Score += 1
                # print(f'{winner} takes the win!')
                self.games[gameNo] = game
                gameOn = False


            if turn >= self.maxTurns:
                # print(game)
                # print("draw")
                self.games[gameNo] = game
                gameOn = False

    def checkConnections(self, move, game):
        play = game[move]
        game = game == play
        search = np.zeros(np.shape(self.searchMask), dtype=int)
        search[:,:,0] = self.searchMask[:,:,0] + move[0]
        search[:,:,1] = self.searchMask[:,:,1] + move[1]
        searchClipped = np.logical_and(np.logical_and(search[:,:,0] >= 0, search[:,:,0] < self.Rows),
                                       np.logical_and(search[:,:,1] >= 0, search[:,:,1] < self.Cols))
        connected = []
        for i in np.arange(4):
            line = game[search[i][searchClipped[i]][:,0],search[i][searchClipped[i]][:,1]]
            line = np.split(line, np.where(np.diff(line) == True)[0] + 1)
            connected.append(sum(max(line, key=sum)))
        return max(connected)

"""
trial = oxGame(player1, player2, 3, 4, 1, 3)

x=1000
while x >= 0:
    trial.runGame(0)
    x -= 1
print(trial.PlayerXScore)
print(trial.Player0Score)

print(f'player1 Func ID: {id(player1)}')
print(f'playerX Func ID: {id(trial.playerX)}')
"""
