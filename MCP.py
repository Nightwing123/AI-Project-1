from search import Problem, Node, path_states, path_actions, breadth_first_search, depth_first_recursive_search, iterative_deepening_search

#An implementation of the Missionary-Cannibal problem
# Tuple format = [<Node (leftMissionaries, rightMissionaries, leftCannibals, rightCannibals, boatSide)>]
class MCP(Problem):
    #state is a tuple(LM,RM,LC,RC,B) with initial value (0,3,0,3,1)
    #last value flips between 1(R) and 0(L)
    LM=0; RM=1; LC=2; RC=3; B=4 #class "constants"

    def __init__(self, initState,goalState):
      Problem.__init__(self, initState, goalState)

    def actions(self, state):
      # In this kind of simple example, it is common to use the new state itself as the action,
      # because it is straightforward and more efficient.
      # We don't do that here just to illustrate how we can denote actions separately from states, if so desired.

      # list of descriptive actions
      list_of_actions=[]
      #temp variables for clarity:
      lm, rm, lc, rc, boat = state[MCP.LM], state[MCP.RM], state[MCP.LC],state[MCP.RC], state[MCP.B]

      if boat == 1: #boat on the right side
        #1ML - can we move 1 Missionary left?
        if self.validate(lm+1, rm-1, lc, rc, 0):
          list_of_actions.append("1ML")
        #2ML - can we move 2 Missionaries left?
        if self.validate(lm+2, rm-2, lc, rc, 0):
          list_of_actions.append("2ML")

        #1CL - can we move one Cannibal left?
        if self.validate(lm ,rm, lc+1, rc-1, 0):
          list_of_actions.append("1CL")

        #2CL - can we move two Cannibals left?
        if self.validate(lm, rm, lc+2, rc-2, 0):
          list_of_actions.append("2CL")

        #1M1CL -  can we move one Missionary and one Cannibal left?
        if self.validate(lm+1, rm-1, lc+1, rc-1, 0):
          list_of_actions.append("1M1CL")

      else:   #boat on the left side
        #1MR - can we move 1 Missionary right?
        if self.validate(lm-1, rm+1, lc, rc, 1):
          list_of_actions.append("1MR")

        #2MR - can we move 2 Missionaries right?
        if self.validate(lm-2, rm+2, lc, rc, 1):
          list_of_actions.append("2MR")

        #1CR - can we move 1 Cannibal right?
        if self.validate(lm, rm, lc-1, rc+1, 1):
          list_of_actions.append("1CR")

        #2CR - can we move 2 Cannibals right?
        if self.validate(lm, rm, lc-2, rc+2, 1):
          list_of_actions.append("2CR")

        #1M1CR-  can we move one Missionary and one Cannibal right?
        if self.validate(lm-1, rm+1, lc-1, rc+1, 1):
          list_of_actions.append("1M1CR")
      
      return list_of_actions

    def validate(self, lm, rm, lc, rc, boat):
        #verify no number is negative
        if lm < 0 or rm < 0 or lc < 0 or rc < 0:
            return False
        #verify no number is greater than the max
        if lm > 3 or rm > 3 or lc > 3 or rc > 3:
            return False
        #verify if boat is on right, then there must be someone on the right side
        if boat == 1 and (rm + rc)==0:
            return False
        #verify if boat is on left, then there must be someone on the left side
        if boat == 0 and (lm + lc)==0:
            return False
        #verify left Missionaries are >= left Cannibals, unless there are no Missionaries on the left
        if lm < lc and lm != 0:
            return False
        #verify right Missionaries are >= right Cannibals, unless there are no Missionaries on the right
        if rm < rc and rm != 0:
            return False
        return True


    def result(self, state, action):
        #Inefficient because we are redoing what we did in actions, but this keeps actions distinct from states
        #Again, temp variables for clarity:
        lm, rm, lc, rc, boat = state[MCP.LM], state[MCP.RM], state[MCP.LC],state[MCP.RC], state[MCP.B]
        #print("ACTION="+action)
        if action=="1ML":
            newState = (lm+1, rm-1, lc, rc, 0)
        elif action=="2ML":
            newState = (lm+2, rm-2, lc, rc, 0)
        elif action=="1CL":
            newState = (lm ,rm, lc+1, rc-1, 0)
        elif action=="2CL":
            newState = (lm, rm, lc+2, rc-2, 0)
        elif action=="1M1CL":
            newState = (lm+1, rm-1, lc+1, rc-1, 0)
        elif action=="1MR":
            newState = (lm-1, rm+1, lc, rc, 1)
        elif action=="2MR":
            newState = (lm-2, rm+2, lc, rc, 1)
        elif action=="1CR":
            newState = (lm, rm, lc-1, rc+1, 1)
        elif action=="2CR":
            newState = (lm, rm, lc-2, rc+2, 1)
        elif action=="1M1CR":
            newState = (lm-1, rm+1, lc-1, rc+1, 1)

        return newState


#Runs the Cannibals and Missionaries problem, will provide a solution to getting all Missionaries
#and all Cannibals to the other side, without Missionaries ever being outnumbered by Cannibals
#on either side.
print('Missionaries/Cannibals Problem: ')
print(' Tuples are in this format --> [<Node (leftMissionaries, rightMissionaries, leftCannibals, rightCannibals, boatSide)>]')
initState = (0,3,0,3,1)
goalState = (3,0,3,0,0)

problem = MCP(initState, goalState)
goal = breadth_first_search(problem)
print("\nPath = ",path_states(goal),"\n\nPath cost = ",goal.path_cost, "\n\nPath actions = ",path_actions(goal))
