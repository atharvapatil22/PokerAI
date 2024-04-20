import random
import copy
from agent import Agent
from player import Action,BetRatio

# This agent can only handle 2player poker. It will have to be modified for multiplayer games.
class MinimaxAgent(Agent):

  # ~~refactor : Similar function is required in round and maybe some other places. This should be refactored to be DRY
  def pos_actions_for_this_player(self,game_state,p_index):
    player_dets = game_state['players'][p_index]
    valid_actions = [Action.FOLD, Action.CALL, Action.CHECK, Action.ALL_IN, Action.LOW_BET, Action.MID_BET, Action.HIGH_BET]
    
    incoming_bet = game_state['currentBet'] - player_dets['bet']
    
    if incoming_bet == 0:
        valid_actions.remove(Action.CALL) 
    if incoming_bet > player_dets['chipsRemaining']:
        if Action.CALL in valid_actions: valid_actions.remove(Action.CALL) 
        valid_actions.remove(Action.LOW_BET)
        valid_actions.remove(Action.MID_BET)
        valid_actions.remove(Action.HIGH_BET)
    if incoming_bet != 0:
        valid_actions.remove(Action.CHECK)
    if incoming_bet > (player_dets['chipsRemaining'] * BetRatio.LOW_BET):
        if Action.LOW_BET in valid_actions: valid_actions.remove(Action.LOW_BET)
    if incoming_bet > (player_dets['chipsRemaining'] * BetRatio.MID_BET):
        if Action.MID_BET in valid_actions: valid_actions.remove(Action.MID_BET)
    if incoming_bet > (player_dets['chipsRemaining'] * BetRatio.HIGH_BET):
        if Action.HIGH_BET in valid_actions: valid_actions.remove(Action.HIGH_BET)
    return valid_actions

  # ~~refactor : Similar logic is used in round Class. This should be refactored to be DRY
  def game_state_after_action(self,game_state,action,p_index):
    new_game_state = copy.deepcopy(game_state)
    player_dets = new_game_state['players'][p_index]
    incoming_bet = new_game_state['currentBet'] - player_dets['bet']
    
    player_dets['acted'] = True
    if action == Action.FOLD:
        new_game_state['players'].pop(p_index)
    elif action == Action.CALL:
        player_dets['bet'] += incoming_bet
        player_dets['chipsRemaining'] -= incoming_bet
        new_game_state['pot'] += incoming_bet
    elif action == Action.ALL_IN:
        player_dets['bet'] += player_dets['chipsRemaining']
        new_game_state['pot'] += player_dets['chipsRemaining']
        if player_dets['chipsRemaining'] > incoming_bet:
            new_game_state['currentBet'] = player_dets['bet']
        player_dets['chipsRemaining'] = 0 
    elif action == Action.LOW_BET:
        player_dets['bet'] += (player_dets['chipsRemaining'] * BetRatio.LOW_BET)
        new_game_state['pot'] += (player_dets['chipsRemaining'] * BetRatio.LOW_BET)
        if (player_dets['chipsRemaining'] * BetRatio.LOW_BET) > incoming_bet:
            new_game_state['currentBet'] = player_dets['bet']
        player_dets['chipsRemaining'] -= (player_dets['chipsRemaining'] * BetRatio.LOW_BET)
    elif action == Action.MID_BET:
        player_dets['bet'] += (player_dets['chipsRemaining'] * BetRatio.MID_BET)
        new_game_state['pot'] += (player_dets['chipsRemaining'] * BetRatio.MID_BET)
        if (player_dets['chipsRemaining'] * BetRatio.MID_BET) > incoming_bet:
            new_game_state['currentBet'] = player_dets['bet']
        player_dets['chipsRemaining'] -= (player_dets['chipsRemaining'] * BetRatio.MID_BET)
    elif action == Action.HIGH_BET:
        player_dets['bet'] += (player_dets['chipsRemaining'] * BetRatio.HIGH_BET)
        new_game_state['pot'] += (player_dets['chipsRemaining'] * BetRatio.HIGH_BET)
        if (player_dets['chipsRemaining'] * BetRatio.HIGH_BET) > incoming_bet:
            new_game_state['currentBet'] = player_dets['bet']
        player_dets['chipsRemaining'] -= (player_dets['chipsRemaining'] * BetRatio.HIGH_BET)
            
    return new_game_state
  
  def is_terminal_state(self,game_state):
    if len(game_state['players']) == 1: return True
    for p in game_state['players']:
        if p['acted']==False or (p['bet'] != game_state['currentBet'] and p['chipsRemaining']>0):
            return False
    return True

  def minimax_search(self,game_state):
    v,action = self.max_value(game_state,0)
    return action
  
  def max_value(self,game_state,level):
    if self.is_terminal_state(game_state):
        print("is terminal")
        return random.randint(0,100), None
    
    v = float('-inf')
    action = None
    
    # possible actions 
    pos_actz = self.pos_actions_for_this_player(game_state,0)
    print("poz act",pos_actz)
    for ac in pos_actz:
        print("\nlevel",level)
        print("Player #0",ac)
        new_gs = self.game_state_after_action(game_state,ac,0)
        v2,a2 = self.min_value(new_gs,level+1)
        if v2>v:
            v,action = v2, a2
    return v,action
  
  def min_value(self,game_state,level):
    if self.is_terminal_state(game_state):
        print("is terminal")
        return random.randint(0,100), None
    v = float('inf')
    action = None
    pos_actz = self.pos_actions_for_this_player(game_state,1)
    print("poz act",pos_actz)
    for ac in pos_actz:
        print("\nlevel",level)
        print("Player #1",ac)
        new_gs = self.game_state_after_action(game_state,ac,1)
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