import oxGameClassified as oxGame
import oxAI
import numpy as np
import oxTrainingTools as oxTT
import pandas as pd

""" Find the best O and X player from previously saved Data"""
topOPlayersLoaded = pd.DataFrame(oxTT.load_topOPlayers())
topXPlayersLoaded = pd.DataFrame(oxTT.load_topXPlayers())
topPlayersLoaded = pd.concat([topXPlayersLoaded, topOPlayersLoaded])
topPlayersLoaded = topPlayersLoaded.reset_index()
del topPlayersLoaded['index']

OPlayers, XPlayers = oxTT.gameOfGames(topPlayersLoaded, topPlayersLoaded)
XPlayersRanked = oxTT.load_players('XPlayersRanked')
OPlayersRanked = oxTT.load_players('OPlayersRanked')

OPlayersRanked = OPlayers.sort_values(by='score', ascending=False, ignore_index=True)
del OPlayersRanked['index']

XPlayersRanked = XPlayers.sort_values(by='score', ascending=False, ignore_index=True)
del XPlayersRanked['index']
XPlayersRanked
XPlayersRanked.loc[0:3]

group = 2
a = np.arange(0,50,group)
refinedPlayers = pd.DataFrame(columns=['AI', 'score'])
for i in a:
    newRefinedPlayers = oxTT.refinePlayers(XPlayersRanked.loc[i:i+group],
                                    topPlayersLoaded,
                                    batchSize=60,
                                    refineXPlayers=True)
    refinedPlayers = pd.concat([refinedPlayers, newRefinedPlayers]).reset_index(drop=True)

refinedPlayers
oxTT.save_players(refinedPlayers, "refinedPlayers3")
oxTT.save_players(XPlayersRanked, "XPlayersRanked")
oxTT.save_players(OPlayersRanked, "OPlayersRanked")

oxGame.oxGame(refinedPlayers.loc[40,'AI'], oxTT.humanPlayer,3,3,1,3).runGame(0)
