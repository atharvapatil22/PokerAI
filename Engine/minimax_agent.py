from agent import Agent
import random

class MinimaxAgent(Agent):

  
  def minimax_search(self,game_state):
    v,action = self.max_value(game_state,0)
    return action
  
  def max_value(self,game_state,level):
    if is_terminal_state(game_state):
        print("is terminal")
        return random.randint(0,100), None
    
    v = float('-inf')
    action = None
    
    # possible actions 
    pos_actz = pos_actions_for_this_player(game_state,0)
    print("poz act",pos_actz)
    for ac in pos_actz:
        print("\nlevel",level)
        print("Player #0",ac)
        new_gs = game_state_after_action(game_state,ac,0)
        v2,a2 = self.min_value(new_gs,level+1)
        if v2>v:
            v,action = v2, a2
    return v,action
  
  def min_value(self,game_state,level):
    if is_terminal_state(game_state):
        print("is terminal")
        return random.randint(0,100), None
    v = float('inf')
    action = None
    pos_actz = pos_actions_for_this_player(game_state,1)
    print("poz act",pos_actz)
    for ac in pos_actz:
        print("\nlevel",level)
        print("Player #1",ac)
        new_gs = game_state_after_action(game_state,ac,1)
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