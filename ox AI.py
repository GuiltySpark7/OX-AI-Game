import oxGameClassified as oxGame




test = oxGame.oxGame(oxGame.player1, oxGame.player2, 3, 4, 1, 3)



x=10000
while x >= 0:
    test.runGame(0)
    x -= 1
print(test.PlayerXScore)
print(test.Player0Score)
