import random
import copy
from agent import Agent
from player import Action,BetRatio

# This agent can only handle 2player poker. It will have to be modified for multiplayer games.
class MinimaxAgent(Agent):

  # ~~refactor : Similar function is required in round and maybe some other places. This should be refactored to be DRY
  # def: Function will return possible actions for a player at this game_state
  def possiblePlayerActions(self,game_state,p_index):
    playerData = game_state['players'][p_index]
    validActions = [Action.FOLD, Action.CALL, Action.CHECK, Action.ALL_IN, Action.LOW_BET, Action.MID_BET, Action.HIGH_BET]
    
    incomingBet = game_state['currentBet'] - playerData['bet']
    
    if incomingBet == 0:
        validActions.remove(Action.CALL) 
    if incomingBet > playerData['chipsRemaining']:
        if Action.CALL in validActions: validActions.remove(Action.CALL) 
        validActions.remove(Action.LOW_BET)
        validActions.remove(Action.MID_BET)
        validActions.remove(Action.HIGH_BET)
    if incomingBet != 0:
        validActions.remove(Action.CHECK)
    if incomingBet > (playerData['chipsRemaining'] * BetRatio.LOW_BET):
        if Action.LOW_BET in validActions: validActions.remove(Action.LOW_BET)
    if incomingBet > (playerData['chipsRemaining'] * BetRatio.MID_BET):
        if Action.MID_BET in validActions: validActions.remove(Action.MID_BET)
    if incomingBet > (playerData['chipsRemaining'] * BetRatio.HIGH_BET):
        if Action.HIGH_BET in validActions: validActions.remove(Action.HIGH_BET)
    return validActions

  # ~~refactor : Similar logic is used in round Class. This should be refactored to be DRY
  # def: Takes in game_state and player action, and returns updated game state (without modifying the current gs)
  def getUpdatedGameState(self,game_state,action,p_index):
    new_game_state = copy.deepcopy(game_state)
    playerData = new_game_state['players'][p_index]
    incomingBet = new_game_state['currentBet'] - playerData['bet']
    
    playerData['acted'] = True
    if action == Action.FOLD:
        new_game_state['players'].pop(p_index)
    elif action == Action.CALL:
        playerData['bet'] += incomingBet
        playerData['chipsRemaining'] -= incomingBet
        new_game_state['pot'] += incomingBet
    elif action == Action.ALL_IN:
        playerData['bet'] += playerData['chipsRemaining']
        new_game_state['pot'] += playerData['chipsRemaining']
        if playerData['chipsRemaining'] > incomingBet:
            new_game_state['currentBet'] = playerData['bet']
        playerData['chipsRemaining'] = 0 
    elif action == Action.LOW_BET:
        playerData['bet'] += (playerData['chipsRemaining'] * BetRatio.LOW_BET)
        new_game_state['pot'] += (playerData['chipsRemaining'] * BetRatio.LOW_BET)
        if (playerData['chipsRemaining'] * BetRatio.LOW_BET) > incomingBet:
            new_game_state['currentBet'] = playerData['bet']
        playerData['chipsRemaining'] -= (playerData['chipsRemaining'] * BetRatio.LOW_BET)
    elif action == Action.MID_BET:
        playerData['bet'] += (playerData['chipsRemaining'] * BetRatio.MID_BET)
        new_game_state['pot'] += (playerData['chipsRemaining'] * BetRatio.MID_BET)
        if (playerData['chipsRemaining'] * BetRatio.MID_BET) > incomingBet:
            new_game_state['currentBet'] = playerData['bet']
        playerData['chipsRemaining'] -= (playerData['chipsRemaining'] * BetRatio.MID_BET)
    elif action == Action.HIGH_BET:
        playerData['bet'] += (playerData['chipsRemaining'] * BetRatio.HIGH_BET)
        new_game_state['pot'] += (playerData['chipsRemaining'] * BetRatio.HIGH_BET)
        if (playerData['chipsRemaining'] * BetRatio.HIGH_BET) > incomingBet:
            new_game_state['currentBet'] = playerData['bet']
        playerData['chipsRemaining'] -= (playerData['chipsRemaining'] * BetRatio.HIGH_BET)
            
    return new_game_state
  
  # Checks if a betting-round/phase is over based on game_state
  def isPhaseOver(self,game_state):
    if len(game_state['players']) == 1: return True
    for player in game_state['players']:
        if player['acted']==False or (player['bet'] != game_state['currentBet'] and player['chipsRemaining']>0):
            return False
    return True

  def minimax_search(self,game_state):
    v,action = self.max_value(game_state,0)
    return action
  
  def max_value(self,game_state,level):
    # If game-state marks the end of phase, return utility value
    if self.isPhaseOver(game_state):
        return random.randint(0,100), None
    
    v = float('-inf')
    action = None
    
    # possible actions for maximizing player 
    possibleActions = self.possiblePlayerActions(game_state,0)
    print("poz act",possibleActions)
    for ac in possibleActions:
        print("\nlevel",level)
        print("Player #0",ac)
        new_gs = self.getUpdatedGameState(game_state,ac,0)
        v2,a2 = self.min_value(new_gs,level+1)
        if v2>v:
            v,action = v2, a2
    return v,action
  
  def min_value(self,game_state,level):
    # If game-state marks the end of phase, return utility value
    if self.isPhaseOver(game_state):
        print("is terminal")
        return random.randint(0,100), None
    
    v = float('inf')
    action = None

    # possible actions for minimizing player
    possibleActions = self.possiblePlayerActions(game_state,1)
    print("poz act",possibleActions)
    for ac in possibleActions:
        print("\nlevel",level)
        print("Player #1",ac)
        new_gs = self.getUpdatedGameState(game_state,ac,1)
        v2,a2 = self.max_value(new_gs,level+1)
        if v2 < v:
            v = v2
            action = a2
    return v,action
  
  # In the current implementation, Minimax search is using a different representation of the board called game state. 
  # This function should be removed later and code should be refactored to have same representation between engine and agents
  def make_game_state_from_board(self,board):
    game_state ={}
    game_state['pot'] = board.pot
    game_state['currentBet'] = board.currentBet
    game_state['players'] = []
    for i in range(board.players.__len__()):
      game_state['players'] .append({'bet':board.playerBets[i],'chipsRemaining':board.players[i].chips,'acted':board.playerPassing[i]})

    return game_state
  
  def get_action(self, board, validActions):
    # game_state = {
    # 'players': [{'bet':25,'chipsRemaining':30,'acted':False},{'bet':50,'chipsRemaining':40,'acted':False}],
    # 'pot': 75,
    # 'currentBet':50,
    # }
    game_state = self.make_game_state_from_board(board)

    # NOTE: Current implementation of search will only search till the end of current phase.
    res = self.minimax_search(game_state)
    print("You should take this action",res)
    return 