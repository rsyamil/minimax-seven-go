from go import *
from util import *
from os import path
import random
from math import inf

class MyPlayer:

    def __init__(self, name=[], go=None, piece_type=None, expansion_limit=None, 
                            verbose=None, b_tune=None, w_tune=None):
        self.name = name
        self.verbose = verbose
        self.state = go
        self.piece_type = piece_type
        self.expansion_limit = expansion_limit
        self.values = self.initScore()[0]
        self.sum_values = self.initScore()[1]
        
        #parameters to tune
        self.b_tune = b_tune
        self.w_tune = w_tune
        
        #strategies to choose from
        self.spread = True
        self.aggressive = True
        
    #weight the score of the board depending on location, tested for odds 5x5, 7x7
    def initScore(self):
        #create placeholder of zeros of board size
        size = self.state.size
        mid = int(self.state.size/2) + 1
        values = [([0]*size) for i in range(size)]
        #assign values into the board in a concentric contour
        for i in range(size):
            for j in range(size):
                _i, _j = i, j
                if i >= mid:
                    _i = size-(i+1)
                if j >= mid:
                    _j = size-(j+1)
                values[i][j] = (_i+1)*(_j+1)
        #sum the values in the matrix
        sum_values = 0
        for i in range(size):
            for j in range(size):
                sum_values = sum_values + values[i][j]
        if self.verbose:
            print("Board heuristic score : ", values)
            print("Sum of board heuristic score : ", sum_values)
        return values, sum_values
        
    #heuristic areal score for board, normalized
    def arealScore(self, i, j):
        areal_value = (self.values[i][j]*self.values[i][j])/self.sum_values
        return areal_value
        
    #for random player only (please comment out if not using)
    def getInputRandom(self):
        possible_placements = []
        for i in range(self.state.size):
            for j in range(self.state.size):
                _, valid = self.state.validMove(i=i, j=j, action=None)
                if valid:
                    possible_placements.append((i,j))
        if not possible_placements:
            return "PASS", (-1, -1)
        else:
            return "MOVE", random.choice(possible_placements)
    
    #ITERATIVE DEEPENING
    #returns the appropriate expansion depth, limit by remaining spots open 
    def getDepth(self):
        limit, depth = 1, 0
        _, available_loc_count = self.state.getAvailableLoc()
        while True:
            if limit > self.expansion_limit or depth + self.state.n_moves > self.state.max_moves:
                break
            else:
                limit = limit*available_loc_count  #branching factor
            #only half of the max_moves if for a player
            if 2*depth >= self.state.max_moves:
                break
            #at the next expansion depth, consider that one spot has been taken 
            available_loc_count = available_loc_count - 1
            depth = depth + 1
        return depth -1                                         #CHECK                
         
    #for smart player, minimax with a-b pruning
    def getInputSmart(self):       
        #heuristic at the beginning of the game: populate the center of the game
        mid = int(self.state.size/2)
        if self.state.piece_type == 1 and self.state.n_moves == 0:
            return "MOVE", (mid, mid)
        if self.state.piece_type == 2 and self.state.n_moves == 1:
            if self.state.board[mid][mid] == 0:
                return "MOVE", (mid, mid)
            elif self.state.board[mid][mid] == 1:
                return "MOVE", (mid, mid-1)
            else:
                print("Impossible configuration")
        #recursive call for minimax with pruning, depth of expansion with heuristic
        alpha, beta = -inf, inf
        depth = self.getDepth()
        value, action, loc = self._max(alpha, beta, copy.deepcopy(self.state), depth, self.state.piece_type)
        return action, loc
        
    #set-up the next state to branch into
    def advanceState(self, state, board):
        previous_board, current_board = copy.deepcopy(state.board), copy.deepcopy(board)
        opponent = 3 - state.piece_type             #for next level
        next_state = Go(name="branch", n=state.size, previous_board=previous_board, 
                            current_board=current_board, piece_type=opponent, n_moves=state.n_moves+1) 
        return next_state
        
    #part of the minimax recursive routine
    def _max(self, alpha, beta, state, depth, piece_type):
        #check if the terminal condition is reached or expansion isnot needed
        if state.n_moves == state.max_moves or depth == 0:
            value = self.evaluate(state, depth, piece_type, "TERMINAL")
            return value, "TERMINAL", (-1, -1)
        #get all possible options
        next_loc = (-1, -1)
        action, value, next_value = "MOVE", -inf, -1
        available_loc_list, _ = state.getAvailableLoc()
        #expand for all possible options when action is "MOVE"
        for loc in available_loc_list:
            board, valid = state.validMove(loc[0], loc[1], "MOVE")
            if not valid:
                continue
            #expand on the next state with _min
            next_state = self.advanceState(state, board)
            next_value, _, _ = self._min(alpha, beta, next_state, depth-1, piece_type)
            if next_value > value:
                value, next_loc, action = next_value, loc, "MOVE"
            if value > beta:
                return value, action, next_loc
            if value > alpha:
                alpha = next_value
        #for when "PASS" is the action (for any available locs are)
        next_state = self.advanceState(state, state.board)
        #double "PASS"
        if state.sameBoard(state.previous_board, state.board) and state.sameBoard(next_state.previous_board, next_state.board):
            next_value = self.evaluate(next_state, depth, piece_type, "NOTTERMINAL")
        else:
            next_value, _, _ = self._min(alpha, beta, next_state, depth-1, piece_type)
        if next_value > value:
            value, action = next_value, "PASS"
        if next_value > beta:
            return value, action, next_loc
        if value > alpha:
            alpha = next_value
        return value, action, next_loc
    
    #part of the minimax recursive routine
    def _min(self, alpha, beta, state, depth, piece_type): 
        #check if the terminal condition is reached or expansion isnot needed
        if state.n_moves == state.max_moves or depth == 0:
            value = self.evaluate(state, depth, piece_type, "TERMINAL")
            return value, "TERMINAL", (-1, -1)
        #get all possible options
        next_loc = (-1, -1)
        action, value, next_value = "MOVE", inf, -1
        available_loc_list, _ = state.getAvailableLoc()
        #expand for all possible options when action is "MOVE"
        for loc in available_loc_list:
            board, valid = state.validMove(loc[0], loc[1], "MOVE")
            if not valid:
                continue
            #expand on the next state with _max
            next_state = self.advanceState(state, board)
            next_value, _, _ = self._max(alpha, beta, next_state, depth-1, piece_type)
            if next_value < value:
                value, next_loc, action = next_value, loc, "MOVE"
            if value <= alpha:
                return value, action, next_loc
            beta = min(beta, value)
        #for when "PASS" is the action (for any available locs are)
        next_state = self.advanceState(state, state.board)
        #double "PASS"
        if state.sameBoard(state.previous_board, state.board) and state.sameBoard(next_state.previous_board, next_state.board):
            next_value = self.evaluate(next_state, depth, piece_type, "NOTTERMINAL")
        else:
            next_value, _, _ = self._max(alpha, beta, next_state, depth-1, piece_type)
        if next_value < value:
            value, action = next_value, "PASS"
        if next_value < alpha:
            return value, action, next_loc
        beta = min(beta, value)
        return value, action, next_loc
        
    #aggressive score, loop through the board and calculate liberty for all connected pieces
    def calcAggressiveScore(self, i, j, state, piece_type, allies):
        test_state = copy.deepcopy(state)
        test_state.board[i][j] = piece_type
        allies = test_state.allyBFS(i, j)
        count = 0
        for a in allies:
            neighbors = test_state.detectNeighbors(a[0], a[1])
            for loc in neighbors:
                if test_state.board[loc[0]][loc[1]] == (3 - piece_type):      
                    count = count + 1
        return count
        
    #function to evaluate score at the end of the branch, diff between the two players
    #Black 1('X'): positive values or White 2('O'): negative values
    #scale score by depth (the deeper you go, the more relevant is the board when pruning)
    def evaluate(self, state, depth, piece_type, action):
        terminal = False
        if action == "TERMINAL":
            terminal = True
        opponent = 3 - piece_type
        value = 0
        depth_scaler = (state.max_moves - depth) / state.max_moves
        chi_player = 0
        chi_opponent = 0
        aggressive_player = 0
        aggressive_opponent = 0
        #select different strategy
        spread = self.spread
        aggressive = self.aggressive
        aggressive_player_allies = []
        #loop through each point in the board
        for i in range(state.size):
            for j in range(state.size):
                #if the board is occupied by either player or opponent
                #black is at a disadvantage because of komi, so we scale the score by piece_type
                if state.board[i][j] != 0:
                    if piece_type == 1:
                        if state.board[i][j] == piece_type:
                            value = value + self.arealScore(i, j) / (depth_scaler + self.b_tune)
                            if aggressive and not terminal and (i, j) not in aggressive_player_allies:
                                aggressive_player = aggressive_player + self.calcAggressiveScore(i, j, state, piece_type, aggressive_player_allies)
                        else:
                            value = value - self.arealScore(i, j) / (depth_scaler + self.w_tune)
                    elif piece_type == 2:
                        if state.board[i][j] == piece_type:
                            value = value + self.arealScore(i, j) / (depth_scaler + self.w_tune)
                            if aggressive and not terminal and (i, j) not in aggressive_player_allies:
                                aggressive_player = aggressive_player + self.calcAggressiveScore(i, j, state, piece_type, aggressive_player_allies)
                        else:
                            value = value - self.arealScore(i, j) / (depth_scaler + self.b_tune)   
                    else:
                        print("Error piece_type in evaluate()")
                #strategy: cutting (keep your stones spread to surround opponent)
                else:
                    if spread and not terminal:
                        neighbors = state.detectNeighbors(i, j)
                        for n in neighbors:
                            if state.board[n[0]][n[1]] == piece_type:
                                chi_player = chi_player + self.arealScore(i, j)
                            elif state.board[n[0]][n[1]] == opponent:
                                chi_opponent = chi_opponent - self.arealScore(i, j)
                            else:
                                value = value              
        #account for the strategy above
        if spread and not terminal:
            value = value + (chi_player - chi_opponent)
        if aggressive and not terminal:
            value = value + (aggressive_player - aggressive_opponent)
        #komi compensation 
        if piece_type == 2:
            value = value + state.komi
        else:
            value = value - state.komi

        if self.verbose:
            print("EVALUATING... value : ", value)
            print("EVALUATING... depth : ", depth)
            print("EVALUATING... depth_scaler : ", depth_scaler)
            print("EVALUATING... chi_player : ", chi_player)
            print("EVALUATING... chi_opponent : ", chi_opponent)
            print("EVALUATING... chi_diff : ", chi_player - chi_opponent)
            print("EVALUATING... aggressive_player : ", aggressive_player)
            print("EVALUATING... aggressive_opponent : ", aggressive_opponent)
        return value
        
if __name__ == "__main__":

    #board size
    verbose = False
    N = 7
    expansion_limit = 80000
    b_tune = 0.5
    w_tune = 0.19
    
    #read in the current board, tracked num of moves and set up a Go instance state
    piece_type, previous_board, board = readInput(N)    
    n_moves = readNumMoves(previous_board, N, int(piece_type))
    go = Go(name="my_player", n=N, previous_board=previous_board, 
                            current_board=board, piece_type=piece_type, n_moves=n_moves)
    go.setBoard(piece_type)
    
    #give the go board state to the player, ask and write the next action
    player = MyPlayer(name="my_player", go=go, piece_type=piece_type, 
                            expansion_limit=expansion_limit, verbose=verbose,
                            b_tune=b_tune, w_tune=w_tune)
    action, result = player.getInputSmart()
    writeOutput(action, result)


