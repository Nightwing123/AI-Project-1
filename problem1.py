from search import Problem, breadth_first_search, path_actions, failure
# A frog is trying to get from the top left corner of a pond to a lily pad marked G. The pond is represented as a 5x5 grid, and each cell contains a number that indicates how many spaces the frog can jump in one of the four cardinal directions (up, down, left, right). The frog can only jump in the direction specified by the number in the cell it currently occupies. For example, if the frog is on a cell with the number 3, it can jump three spaces up, down, left, or right (as long as it stays within the bounds of the grid). The goal is to find a sequence of jumps that leads the frog to the lily pad marked G.
class LilyPad(Problem):

    # The size of the grid is 5x5, so we can represent the state as a single integer from 0 to 24, where 0 is the top left corner and 24 is the bottom right corner.
    SIZE = 5

    # The board is represented as a string of 25 characters, where each character is either a digit (1-4) representing the jump distance or 'G' representing the goal.
    def __init__(self, board):
        self.board = board.strip()
        initial = 0
        goal = self.board.index('G')
        Problem.__init__(self, initial, goal)

    # Return the legal moves from this state: U, D, L, R.
    def actions(self, state):
        #Return the legal moves from this state: U, D, L, R.
        current = self.board[state]

        # If we are already on the goal, no actions needed
        if current == 'G':
            return []

        # The jump distance is determined by the number in the current cell
        jump = int(current)
        row = state // LilyPad.SIZE
        col = state % LilyPad.SIZE

        # Calculate the possible moves based on the jump distance and the current position
        moves = []

        # Right
        if col + jump < LilyPad.SIZE:
            moves.append('R')

        # Left
        if col - jump >= 0:
            moves.append('L')

        # Up
        if row - jump >= 0:
            moves.append('U')

        # Down
        if row + jump < LilyPad.SIZE:
            moves.append('D')

        return moves
    
    # Given a state and an action, return the resulting state after taking that action.
    def result(self, state, action):
        #Return the new position after taking the action.
        jump = int(self.board[state])

        # Calculate the new state based on the action
        if action == 'R':
            return state + jump
        elif action == 'L':
            return state - jump
        elif action == 'U':
            return state - LilyPad.SIZE * jump
        elif action == 'D':
            return state + LilyPad.SIZE * jump

        return state



# Change this board string to test other ponds
board_string = "3211142G13211224321321242"

# Create the problem and solve it
problem = LilyPad(board_string)
goal = breadth_first_search(problem)

if goal == failure:
    print("No solution")
else:
    moves = path_actions(goal)
    print("Moves:", "".join(moves))
    print("Steps:", len(moves))