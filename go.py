import sys
import copy
from collections import deque
import pickle

class Go:
    def __init__(self, name=[], n=0, previous_board=None, current_board=None, piece_type=None, n_moves=None):
        self.name = name
        self.size = n
        self.n_moves = n_moves      #keep track of number of moves
        self.max_moves = (n*n)-1    #max steps in the game
        self.dead_pieces = []       #initially empty
        self.komi = n/2.0           #Komi rule for second mover
        
        self.piece_type = piece_type            #chess being played
        self.previous_board = previous_board    #the board after your last mover
        self.board = current_board      #the board after opponents move
        
    #call this after instantiating the Go class to diff current and previous board
    def setBoard(self, piece_type):
        for i in range(self.size):
            for j in range(self.size):
                if self.previous_board[i][j] == piece_type and self.board[i][j] != piece_type:
                    self.dead_pieces.append((i, j))
    
    #function to check if the two boards are the same
    def sameBoard(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if not board1[i][j] == board2[i][j]:
                    return False
        return True
        
    #function to check if the board position is valid
    def validPosition(self, i, j):
        if 0 <= i < self.size and 0 <= j < self.size:
            return True
        return False
        
    #get and count available points on the board
    def getAvailableLoc(self):
        availableLoc = []
        availableLocCount = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    availableLoc.append((i, j))
                    availableLocCount += 1
        return availableLoc, availableLocCount
        
    #calculate the score for any player, 1('X') or 2('O')
    def calcScore(self, piece_type):
        board = self.board
        counter = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    counter += 1
        return counter
        
    #check for winner by getting number of chess and komi rule, 0 if tie
    def judgeWinner(self):
        X_player = self.calcScore(1)
        O_player = self.calcScore(2)
        if X_player > (O_player + self.komi):
            return 1
        elif X_player < (O_player + self.komi):
            return 2
        else:
            return 0
            
    #check if the game ended if (1) max_moves reached (2) double pass
    def gameEnd(self, action="MOVE"):
        if self.sameBoard(self.previous_board, self.board) and action == "PASS":
            return True
        if self.n_moves >= self.max_moves:
            return True
        return False
       
    #update the board
    def updateBoard(self, new_board):
        self.board = new_board
        
    #visualize the board
    def visualizeBoard(self):
        board = self.board
        print('-' * self.size * 2)
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == 0:
                    print(' ', end=' ')
                elif board[i][j] == 1:
                    print('X', end=' ')
                else:
                    print('O', end=' ')
            print()
        print('-' * self.size * 2)
        
    #list all immediate neigbors of a given chess (i, j), consider borders
    def detectNeighbors(self, i, j):
        board = self.board
        neighbors = []
        if i > 0:                           #left neighbor
            neighbors.append((i-1, j))
        if i < (self.size - 1):             #right neighbor
            neighbors.append((i+1, j))
        if j > 0:                           #top neighbor
            neighbors.append((i, j-1))
        if j < (self.size - 1):             #bottom neighbor
            neighbors.append((i, j+1))
        return neighbors
            
    #from detected neighbors, identify allies, or can also call validPosition()
    def detectNeighborsAlly(self, i, j):
        board = self.board
        neighbors = self.detectNeighbors(i, j)
        group_allies = []
        for n in neighbors:
            if board[n[0]][n[1]] == board[i][j]:    #if chess is the same type
                group_allies.append(n)
        return group_allies
        
    #use BFS to search for all unique allies of any given player
    def allyBFS(self, i, j):
        queue = deque()
        queue.append((i, j))
        ally_members = []
        while queue:
            piece = queue.popleft()
            ally_members.append(piece)
            group_allies = self.detectNeighborsAlly(piece[0], piece[1])
            for a in group_allies:
                if a not in ally_members and a not in queue:
                    queue.append(a)
        return ally_members
            
    #check if group of allied chesses has liberty
    def hasLiberty(self, i, j):
        board = self.board
        ally_members = self.allyBFS(i, j)
        for a in ally_members:
            neighbors = self.detectNeighbors(a[0], a[1])
            for loc in neighbors:
                if board[loc[0]][loc[1]] == 0:      #empty space
                    return True
        return False
            
    #function to find dead chesses for any given player, 1('X') or 2('O')
    def findDeadPieces(self, piece_type):
        board = self.board
        dead_pieces = []
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type and not self.hasLiberty(i, j):
                    dead_pieces.append((i, j))
        return dead_pieces
        
    #remove dead pieces for any given player, 1('X') or 2('O')
    #for opponent of a player, opponent = 3 - piece_type
    def removeDeadPieces(self, piece_type):
        board = self.board
        dead_pieces = self.findDeadPieces(piece_type)
        if len(dead_pieces) == 0:
            return []
        else:
            for piece in dead_pieces:
                board[piece[0]][piece[1]] = 0
            self.updateBoard(board)             #not necessary          
        return dead_pieces
    
    #implement moves (i.e. branches by returning copies of GO with amended board)
    #also return True if its a valid move
    def validMove(self, i, j, action):
        opponent = 3 - self.piece_type
        Go_test = copy.deepcopy(self)
        board_test = Go_test.board
        
        #if PASS, nothing changes so return the same copy
        if action == "PASS":
            return board_test, True
            
        #check if i, j is valid
        if not Go_test.board[i][j] == 0:
            return board_test, False
        if not Go_test.validPosition(i, j):
            return board_test, False
        
        #amend the copy of the board
        #check if movement is valid (i.e. has liberty, not suicide) and remove pieces of opponent
        board_test[i][j] = self.piece_type
        if Go_test.hasLiberty(i, j):
            Go_test.removeDeadPieces(opponent)             
            return Go_test.board, True
        #if no liberty, remove dead pieces for opponent and check again
        #this is for case such as
        # . X O . .
        # X . X O .
        # . X O . .
        # . . . . .
        else:
            Go_test.removeDeadPieces(opponent)
            #check for KO rule
            if Go_test.hasLiberty(i, j):
                if self.sameBoard(Go_test.board, self.previous_board):
                    return Go_test.board, False
            else:
                return Go_test.board, False
        return Go_test.board, True
        #CHECK IF I NEED TO CHANGE PREVIOUS_BOARD AND BOARD
        
    #implement moves (i.e. branches by returning copies of GO with amended board)
    #also return True if its a valid move
    def validMoveRandom(self, i, j, action):
        opponent = 3 - self.piece_type
        Go_test = self
        board_test = Go_test.board
        
        #if PASS, nothing changes so return the same copy
        if action == "PASS":
            return board_test, True
            
        #check if i, j is valid
        if not Go_test.board[i][j] == 0:
            return board_test, False
        if not Go_test.validPosition(i, j):
            return board_test, False
        
        #amend the copy of the board
        #check if movement is valid (i.e. has liberty, not suicide) and remove pieces of opponent
        board_test[i][j] = self.piece_type
        if Go_test.hasLiberty(i, j):
            Go_test.removeDeadPieces(opponent)             
            return Go_test.board, True
        #if no liberty, remove dead pieces for opponent and check again
        #this is for case such as
        # . X O . .
        # X . X O .
        # . X O . .
        # . . . . .
        else:
            Go_test.removeDeadPieces(opponent)
            #check for KO rule
            if Go_test.hasLiberty(i, j):
                if self.sameBoard(Go_test.board, self.previous_board):
                    return Go_test.board, False
            else:
                return Go_test.board, False
        return Go_test.board, True
        #CHECK IF I NEED TO CHANGE PREVIOUS_BOARD AND BOARD
            
        
        
        
        
        
        
    
        
    
        
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    
        
            
        
        
        
    
        






























