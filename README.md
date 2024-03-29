# minimax-seven-go

This is my Python implementation of a minimax AI agent :robot: for a game of Go with board dimension of 7x7. The minimax agent can be played as Black or White stone with a random agent. To run, clone the repository and bash:

> $ sh build.sh

Here is an example of a game when playing as a Black stone (i.e. first player) using the first three heuristics against a random agent playing the White stone. The board can be scaled-up to 19x19, however computation overhead remains a limiting factor. X represents the Black stones and O represents the white stones. The game mechanism is simple, each agent reads an input file that contains the current and previous board, then decide what the next move is by writing the location coordinate into an output file. The usual [liberty rule, KO rule and komi compensation apply.](https://en.wikipedia.org/wiki/Rules_of_Go)

![Game](/readme/game_progression.png)

To help reduce the search space and for improved efficiency, some of the [following heuristics](https://en.wikipedia.org/wiki/Go_strategy_and_tactics) are built into the AI agent :robot::
* **Iterative deepening** - with a dimension of 7x7, there are 3^49 possible states and it is simply impossible (at least on the hardware that I have) to search all the states towards the terminal states. In lieu of this, at the start of the game we will search a shallower depth and later in the game, we will march on all the way to the terminal states. 
* **Areal scoring** - in the Go game of original dimension 19x19, there are strategic locations to open the game and they are located at the corners of the board. However in this smaller Go game of dimension 7x7, we will give higher score to the center of the board to encourage the AI agent to surround the opponents to the corners of the board. The areal scores contour towards the edges of the board.
* **Score scaling** - the White player are given komi compensation for starting second, and this can put the AI agent at a disadvantage when playing as the Black player. When calculating the value of each instance of the board as the agent branches to all possible states within the specified depth, we scale the score of black and white stones to handle the komi compensation. 
* **Aggressive and spread** - We can favor moves that will maximize the liberty of the player and minimize the liberty of the opponent (i.e. aggressive). The logic here is such that, it may make more sense to form a thick elongated front of stones rather than a square blob and to also capture the opponent's stones. This needs further testing. In `my_player.py` this can be switched on or off using the `spread` and `aggressive` atrributes. 

Here is an example of a game when aggressive mode is on. Note the difference in stone placement compared to the first image. 
![Game2](/readme/game_progression_aggressive.png)

And here is an example of a game when the agressive and spread mode are both on. The stones are not as concentrated as in the first image and are actively trying to capture the opponent's stones, rather than trying to push the opponent's stones to the corner.  
![Game3](/readme/game_progression_aggressive_spread.png)

These heuristics seem to work well with a small Go board but will need to be modified when the board size is larger. For example, a board of 19x19 can have areal scoring contour with multiple peaks (i.e. near each corner and at the center). 
