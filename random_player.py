import random
import sys
from host import GO

def readInput(n, path="input.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()

        piece_type = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]

        return piece_type, previous_board, board

def writeOutput(result, path="output.txt"):
    res = ""
    if result == "PASS":
    	res = "PASS"
    else:
	    res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)

def writePass(path="output.txt"):
	with open(path, 'w') as f:
		f.write("PASS")
        
class RandomPlayer():
    def __init__(self):
        self.type = 'random'

    def get_input(self, go, piece_type):      
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))

        if not possible_placements:
            return "PASS"
        else:
            return random.choice(possible_placements)

if __name__ == "__main__":
    N = 7
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = RandomPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)