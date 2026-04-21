from search import Problem, astar_search, path_states, path_actions, failure

# A* search with a custom heuristic for the Red-Green puzzle.
class RedGreenPuzzle(Problem):
    SIZE = 5
    N = 25


    # The board is represented as a string of 25 characters, where each character is either '1' (red) or '0' (green).
    def __init__(self, board_string):
        # Precompute toggle masks for each button and row/column masks for heuristics
        #Toggle masks indicate which cells are toggled when a specific button is pressed.
        self.toggle_masks = self.make_toggle_masks()
        self.row_masks = self.make_row_masks()
        self.col_masks = self.make_col_masks()

        # state = (board_bits, next_button_index)
        initial = (self.string_to_bits(board_string), 0)
        Problem.__init__(self, initial, None)


    # Each button toggles its own cell and the four orthogonally adjacent cells.
    def make_toggle_masks(self):
        masks = []
        for i in range(RedGreenPuzzle.N):
            r = i // RedGreenPuzzle.SIZE
            c = i % RedGreenPuzzle.SIZE
            mask = 0

            positions = [
                (r, c),
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1)
            ]

            for rr, cc in positions:
                if 0 <= rr < RedGreenPuzzle.SIZE and 0 <= cc < RedGreenPuzzle.SIZE:
                    idx = rr * RedGreenPuzzle.SIZE + cc
                    mask |= (1 << idx)

            masks.append(mask)
        return masks


    # Masks for rows and columns to help with heuristics
    def make_row_masks(self):
        masks = []
        for r in range(RedGreenPuzzle.SIZE):
            mask = 0
            for c in range(RedGreenPuzzle.SIZE):
                idx = r * RedGreenPuzzle.SIZE + c
                mask |= (1 << idx)
            masks.append(mask)
        return masks


    # Masks for columns to help with heuristics
    def make_col_masks(self):
        masks = []
        for c in range(RedGreenPuzzle.SIZE):
            mask = 0
            for r in range(RedGreenPuzzle.SIZE):
                idx = r * RedGreenPuzzle.SIZE + c
                mask |= (1 << idx)
            masks.append(mask)
        return masks

    # Convert the board string to a bit representation (1 for red, 0 for green).
    def string_to_bits(self, s):
        s = s.strip().replace("\n", "")
        bits = 0
        for i in range(len(s)):
            if s[i] == '1':
                bits |= (1 << i)
        return bits

    # The goal is to have all cells green (0 bits).
    def is_goal(self, state):
        board_bits, next_button = state
        return board_bits == 0

    # Actions are "SKIP" or "PRESS" for the next button in sequence.
    def actions(self, state):
        board_bits, next_button = state
        if next_button >= RedGreenPuzzle.N:
            return []
        return ["SKIP", "PRESS"]

    # Given a state and an action, return the resulting state after taking that action.
    def result(self, state, action):
        board_bits, next_button = state

        if action == "SKIP":
            return (board_bits, next_button + 1)
        else:
            new_bits = board_bits ^ self.toggle_masks[next_button]
            return (new_bits, next_button + 1)

    # The cost of pressing a button is 1, while skipping has no cost.
    def action_cost(self, s, a, s1):
        if a == "SKIP":
            return 0
        return 1

    # Heuristic: Estimate the number of presses needed based on the number of red cells.
    def h1(self, node):
        board_bits, next_button = node.state
        red_count = board_bits.bit_count()
        return (red_count + 4) // 5

    # Improved heuristic: Consider the distribution of red cells across rows and columns.
    def h2(self, node):
        
        # borard bits is a 25-bit integer where each bit represents a cell (1 for red, 0 for green).
        #next_button is the index of the next button to consider pressing (0 to 24).
        board_bits, next_button = node.state

        # Count how many rows and columns have at least one red cell, since each press can affect multiple cells in a row/column.
        rows_with_red = 0
        for mask in self.row_masks:
            if board_bits & mask:
                rows_with_red += 1

        # Count how many columns have at least one red cell, since each press can affect multiple cells in a row/column.
        cols_with_red = 0
        for mask in self.col_masks:
            if board_bits & mask:
                cols_with_red += 1

        return max(rows_with_red, cols_with_red)

    # The Problem class defines the structure of a search problem, including methods for
    def h(self, node):
        return self.h2(node)

    # This method solves the puzzle using a linear algebra approach over GF(2) instead of A* search, which is much faster for this type of problem.
    def solve_linear(self):
        
        n = RedGreenPuzzle.N

        # Build matrix A (n x n) where A[row][col]=1 if pressing button col toggles cell row
        A = [[0] * n for _ in range(n)]
        for col in range(n):
            mask = self.toggle_masks[col]
            for row in range(n):
                if (mask >> row) & 1:
                    A[row][col] = 1

        # RHS vector b: initial board bits
        b = [(self.initial[0] >> row) & 1 for row in range(n)]

        # Augmented matrix mat = [A | b]
        mat = [A[row][:] + [b[row]] for row in range(n)]

        # Gaussian elimination over GF(2)
        pivots = [-1] * n
        row = 0
        for col in range(n):
            # find pivot
            sel = None
            for r in range(row, n):
                if mat[r][col] == 1:
                    sel = r
                    break
            if sel is None:
                continue
            mat[row], mat[sel] = mat[sel], mat[row]
            pivots[col] = row

            # eliminate other rows
            for r in range(n):
                if r != row and mat[r][col] == 1:
                    for c in range(col, n + 1):
                        mat[r][c] ^= mat[row][c]
            row += 1
            if row == n:
                break

        # Check for inconsistency (0 = 1)
        for r in range(row, n):
            if all(mat[r][c] == 0 for c in range(n)) and mat[r][n] == 1:
                return None

        # Back substitution / build one particular solution (free variables = 0)
        x0 = [0] * n
        for col in range(n - 1, -1, -1):
            r = pivots[col]
            if r == -1:
                x0[col] = 0
            else:
                s = mat[r][n]
                for c in range(col + 1, n):
                    s ^= (mat[r][c] & x0[c])
                x0[col] = s

        # Build nullspace basis vectors for free variables
        free_cols = [c for c in range(n) if pivots[c] == -1]
        basis = []
        for f in free_cols:
            v = [0] * n
            v[f] = 1
            for col in range(n):
                r = pivots[col]
                if r != -1:
                    # in RREF, mat[r][f] is the coefficient of free var f in eq for pivot col
                    v[col] = mat[r][f]
            basis.append(v)

        # If nullspace small, search all combinations for minimal weight solution
        k = len(basis)
        if k == 0:
            x_best = x0
        elif k <= 20:
            best_weight = n + 1
            x_best = None
            for mask in range(1 << k):
                x = x0[:]  # start from particular solution
                for j in range(k):
                    if (mask >> j) & 1:
                        # XOR basis vector
                        bj = basis[j]
                        for idx in range(n):
                            x[idx] ^= bj[idx]
                w = sum(x)
                if w < best_weight:
                    best_weight = w
                    x_best = x
        else:
            # Nullspace too large to brute-force; return particular solution (fast fallback)
            x_best = x0

        presses = [i for i, v in enumerate(x_best) if v == 1]
        return presses

# Helper functions to visualize the board and the presses
def board5(state):
    board_bits, next_button = state
    rows = []

    for r in range(5):
        row = ""
        for c in range(5):
            idx = r * 5 + c
            if (board_bits >> idx) & 1:
                row += "1"
            else:
                row += "0"
        rows.append(row)

    return "\n".join(rows)

# Convert a list of actions ("SKIP"/"PRESS") to the corresponding button indices that were pressed.
def pressed_buttons(actions):
    result = []
    button = 0

    for action in actions:
        if action == "PRESS":
            result.append(button)
        button += 1

    return result

# Change this board string to test other puzzles
board_string = "1100011100101100010101110"

problem = RedGreenPuzzle(board_string)

# Run A*  with heuristic h2 to solve the puzzle and print the solution path and pressed buttons.
goal = astar_search(problem, h=problem.h2)

if goal == failure:
    print("No solution")
else:
    print("Intermediate states:\n")
    for state in path_states(goal):
        print(board5(state))
        print()

    actions = path_actions(goal)
    presses = pressed_buttons(actions)

    print("Steps:", len(presses))