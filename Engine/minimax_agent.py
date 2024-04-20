import random
import copy
from agent import Agent

class MinimaxAgent(Agent):

  def pos_actions_for_this_player(self,game_state,p_index):
    player_dets = game_state['players'][p_index]
    valid_actions = ['FOLD','CALL','CHECK','ALLIN','LOWBET','MEDBET','HIGHBET']
    
    incoming_bet = game_state['top_bet'] - player_dets['cur_bet']
    
    if incoming_bet == 0:
        valid_actions.remove("CALL") 
    if incoming_bet > player_dets['chips_remaining']:
        if "CALL" in valid_actions: valid_actions.remove("CALL") 
        valid_actions.remove("LOWBET")
        valid_actions.remove("MEDBET")
        valid_actions.remove("HIGHBET")
    if incoming_bet != 0:
        valid_actions.remove('CHECK')
    if incoming_bet > player_dets['chips_remaining'] * 0.1:
        if "LOWBET" in valid_actions: valid_actions.remove('LOWBET')
    if incoming_bet > player_dets['chips_remaining'] * 0.4:
        if "MEDBET" in valid_actions: valid_actions.remove('MEDBET')
    if incoming_bet > player_dets['chips_remaining'] * 0.7:
        if "HIGHBET" in valid_actions: valid_actions.remove('HIGHBET')
    return valid_actions

  def game_state_after_action(self,game_state,action,p_index):
    new_game_state = copy.deepcopy(game_state)
    player_dets = new_game_state['players'][p_index]
    incoming_bet = new_game_state['top_bet'] - player_dets['cur_bet']
    
    player_dets['acted'] = True
    if action == 'FOLD':
        new_game_state['players'].pop(p_index)
    elif action == 'CALL':
        player_dets['cur_bet'] += incoming_bet
        player_dets['chips_remaining'] -= incoming_bet
        new_game_state['pot'] += incoming_bet
    elif action == 'ALLIN':
        player_dets['cur_bet'] += player_dets['chips_remaining']
        new_game_state['pot'] += player_dets['chips_remaining']
        if player_dets['chips_remaining'] > incoming_bet:
            new_game_state['top_bet'] = player_dets['cur_bet']
        player_dets['chips_remaining'] = 0 
    elif action == 'LOWBET':
        player_dets['cur_bet'] += (player_dets['chips_remaining'] * 0.1)
        new_game_state['pot'] += (player_dets['chips_remaining'] * 0.1)
        if (player_dets['chips_remaining'] * 0.1) > incoming_bet:
            new_game_state['top_bet'] = player_dets['cur_bet']
        player_dets['chips_remaining'] -= (player_dets['chips_remaining'] * 0.1)
    elif action == 'MEDBET':
        player_dets['cur_bet'] += (player_dets['chips_remaining'] * 0.4)
        new_game_state['pot'] += (player_dets['chips_remaining'] * 0.4)
        if (player_dets['chips_remaining'] * 0.4) > incoming_bet:
            new_game_state['top_bet'] = player_dets['cur_bet']
        player_dets['chips_remaining'] -= (player_dets['chips_remaining'] * 0.4)
    elif action == 'HIGHBET':
        player_dets['cur_bet'] += (player_dets['chips_remaining'] * 0.7)
        new_game_state['pot'] += (player_dets['chips_remaining'] * 0.7)
        if (player_dets['chips_remaining'] * 0.7) > incoming_bet:
            new_game_state['top_bet'] = player_dets['cur_bet']
        player_dets['chips_remaining'] -= (player_dets['chips_remaining'] * 0.7)
            
    return new_game_state
  
  def is_terminal_state(self,game_state):
    if len(game_state['players']) == 1: return True
    for p in game_state['players']:
        if p['acted']==False or (p['cur_bet'] != game_state['top_bet'] and p['chips_remaining']>0):
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
  
  def get_action(self, board, validActions):
    game_state = {
    'players': [{'cur_bet':25,'chips_remaining':30,'acted':False},{'cur_bet':50,'chips_remaining':40,'acted':False}],
    'pot': 75,
    'top_bet':50,
    }

    res = self.minimax_search(game_state)
    print("You should take this action",res)
    return 