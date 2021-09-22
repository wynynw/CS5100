#----- IFN680 Assignment 1 -----------------------------------------------#
#  The Wumpus World: a probability based agent
#       (the main program)
#
#-----Statement of Authorship----------------------------------------#
#
#  By submitting this code I agree that it represents my own work. 
#  I am aware of the University rule that a student must not act in 
#  a manner which constitutes academic dishonesty as stated and 
#  explained in QUT's Manual of Policies and Procedures, Section C/5.3
#  "Academic Integrity" and Section E/2.1 "Student Code of Conduct".
#
#    Student no: PUT YOUR STUDENT NUMBER HERE
#    Student name: PUT YOUR NAME HERE
#
#--------------------------------------------------------------------#
#
#  This is the provided Python package for the first IFN680 assignment.
#  The code in this file contains three Python classes, Robot, Cave and GUI,
#  and the main program to start the game.
#
#  Class Cave defines the cave environment board, class Robot defines the agent,
#  and class GUI defines the Graphical User Interface to display the moves
#  conduct interaction with the user, start and end the game.
#
#  This code is provided to facilitate you in developing, running and
#  testing your code. You can use any of the functions and variables defined in
#  this program via objects of these classes. BUT, you cannot use any of the 
#  following three protected variables of class Cave in any way in your code:
#
#               _goldCoor, _wumpusCoor, and _pitCoors
#
#  If you have used any of the three variables in your code, significant mark deduction
#  to your submission will be applied.
#
#  Basically you cannot make any change to the code in this file. The only exceptional
#  case is when you have defined additional functions in your probability_based_move.py  
#  except for the required functions. In this case, you need to link these additional
#  functions at the beginning of class Robot. 
#  
#  If you find any problem or you think any change to the code below is needed,
#  please contact Yue before you make the change. Any change without discussing with Yue
#  will potentially cause mark deduction to your submission. 
#  
#  This program was developed by Yunshi Sun and Yue Xu.
#  If you encounter any problem in terms of using the program, please
#  contact Yue by email: yue.xu@qut.edu.au
#___________________________________________________________________________________________________________________________

from tkinter import *
from random import *
from IFN680_AIMA.logic import *
from IFN680_AIMA.utils import *
from IFN680_AIMA.probability import *
from PIL import Image, ImageTk
import tkinter.messagebox,time
# Python 2.7, ttk provides Combobox
from tkinter.ttk import *

import logic_based_move
import probability_based_move

#---------------------------------------------------------------------------------------------------
#
#Global constrants
T, F = True, False
board_height = 600 # height of the board window
board_width = 600 # width of the board window

# # Global variables
# fixed_board = False # the board configuration is fixed or random

#___________________________________________________________________________________________________________________________

class Robot():
    
    ## Link the function, next_room(), that has been defined in the provided file logic_based_move.py
    ## This function is the only function in the logic_based_move module
    next_room = logic_based_move.next_room
    
    ## Link the function, next_room_prob(), that is to be defined by you in the file probability_based_move.py
    next_room_prob = probability_based_move.next_room_prob

    ## Link the function, PitWumpus_prob_distribution(), that is to be defined by you in the file probability_based_move.py
    PitWumpus_probability_distribution = probability_based_move.PitWumpus_probability_distribution  

    ## If you have defined more functions in your probability_based_move.py,
    ## please link them below, this is the ONLY place that you can make change to the code


# ---------------------------------------------------------------------------------------------

    # This is the constructor to create an object of Robot
    def __init__(self,cave):
        self.cave = cave # The cave environment, it is an object of Cave, the cave object that the robot is in  
        self.kb = PropKB() # The robot's knowledge base which is an object of PropKB, it is used by the logic based agent.
        self.visited_rooms = set() # A set of room locations which have been visited by the robot so far.
                                   # Each location is a pair of column and row, e.g., visited_rooms = {(1,3), (1,2), (2,3)}
        self.available_rooms=set() # A set of room locations currently available, but may or may not be directly accessible to the robot.
        self.gold_collected = False # A Boolean variable indicating whether the robot has collected the gold or not
        self.gameover = False # A Boolean variable indicating whether the game is over or not
        self.dead = False # A Boolean variable indicating whether the robot is dead or still alive
        self.win = False # A Boolean variable indicating whether the robot has won the game or not
        self.path = [] # A list of room locations that have been visited by the robot so far.
                       # The first (i.e., the left-most) (column, row) pair is the first room that the robot has visited.
                       # It may contain duplicates, which means some of the locations may have been visited more than one time due to backtracking.
        self.num_moves = 0 # The number of moves the robot has made
        self.max_pit_probability = 0 # The maximum probability threshold
                                     # If the probability of a room containing a pit/wumpus is larger than this threshold, this room is considered unsafe
                                     # and should not be chosen for next move.

        self.move(1,self.cave.HEIGHT) # call the move() function to set the robot at the starting point (1, self.HEIGHT)
                                      # and initialize: self.visited_rooms = {(1, self.HEIGHT)}, self.path=[(1, self.HEIGHT)], self.num_moves=1
                                      #                 self.available_rooms = get.surrounding(1, self.HEIGHT) which are (2,self.HEIGHT) and (1,self.HEIGHT-1)

        # Build the joint probability distribution of pits/wumpus configurations in the given cave environment.
        # The function PitWumpus_probability_distribution()is defined in probability_based_move.py
        self.PitWumpus_probability_distribution(self.cave.WIDTH, self.cave.HEIGHT)
                
#---------------------------------------------------------------------------------------------------

    ## Move the robot to (column,row) and return the new location 
    def move(self, column, row):
        #check if it is moving back to a visited room
        if (column,row) in self.path:
            self.path.pop() # remove (column,row) from path
        else:
            self.path.append((column,row))
            
        self.current_position = (column,row) # update robot current_position
        self.num_moves +=1 # Count the number of moves

        ## if (column,row) is a room which has not been visited, add the location to the visied set
        ## and add logic expression concerning stench and breeze to the knowledge base which is for the logic based agent
        if (column,row) not in self.visited_rooms:
            self.visited_rooms.add((column,row))
            self.kb_add(column,row)
            ## remove it from available_rooms set if it is in available_rooms
            if (column,row) in self.available_rooms:
                self.available_rooms.remove((column,row))
            
            ## Check each of the surrounding rooms of (column,row)
            ##      if it has not been visited, add it to the available_room set
            for each_s in self.cave.getsurrounding(column,row):
                if each_s not in self.visited_rooms:
                    self.available_rooms.add(each_s)
        
        return self.current_position

#---------------------------------------------------------------------------------------------------       
    def step(self, agent_type, max_prob):
        # This method is to invoke the selected agent and use it to determine which room the robot should move to,
        # and also determine whether the game is over or not.
        # 
        # agent_type: an integer, indicate which agent has been chosen by the user
        #             if agent_type = 0, the logic based agent was chosen
        #             if agent_type = 1, the probability based agent was chosen
        # max_prob: an floating number, it is the maximum probability threshold specified by the user

        # Get the maximum probability threshold. 
        self.max_pit_probability = max_prob

        # Two functions can be used to determine the next room: next_room() and next_room_prob()
        # If agent_type = 0, function next_room() will be called. It is an existing function included in the provided program.
        # This function finds a safe room by using the logic resolution method.
        # 
        # For this assignment, you are required to develop the new method: next_room_prob().
        # When agent_type = 1, your function next_room_prob() will be called.
        # It should choose a room which has the lowest probability that the room has a pit or the wumpus
        
        # functions = {0: self.next_room, 1: self.next_room_prob}
        functions = {0: self.next_room_prob, 1: self.next_room}
        checking_function = functions.get(agent_type) 

        # Check if the game is over
        if (self.gold_collected == False and len(self.available_rooms)==0) or self.dead == True: # no more rooms
            self.gameover = True
            return self.current_position
        if self.gameover == False and self.gold_collected == False: # if game is not over and gold not yet collected 
            new_room = checking_function(self.current_position[0], self.current_position[1])
            print('new_room:',new_room)
            if not (new_room[0]== 0 and new_room[1]==0): ## Move to the new room if there is one  
                self.move(new_room[0],new_room[1])
                return self.current_position
            else: ## if there is no rooms available
                  ## backtrack one position
                if len(self.path)==0: ## if no rooms to backtrack, game is over
                    self.gameover = True
                    return self.current_position
                else:
                    next_room = self.path[len(self.path)-2] # backtrack one position
                    self.move(next_room[0],next_room[1])
                    return self.current_position

#---------------------------------------------------------------------------------------------------
    #
    ## This method is to check whether a room at (column,row) has breeze.
    ## (column,row) must be a room which has been visied by the robot.
    def has_breeze(self, column, row):
        # only allow to check positions in visited set or the current position
        if (column,row) in self.visited_rooms or (column==self.current_position[0] and row == self.current_position[1]):
            if self.cave.has_breeze(column,row) == True:
                return True
            else:
                return False
        else:
            tkinter.messagebox.showinfo("Errors", "The position has not been visited yet.")
            return False
        
#---------------------------------------------------------------------------------------------------
    ## This method is to check whether a room at (column,row) has stench.
    ## (column,row) must be a room which has been visied by the robot.
    def has_stench(self, column, row):
        # only allow to check positions in visited set or the current position
        if ((column,row) in self.visited_rooms) or (column==self.current_position[0] and row == self.current_position[1]):
            if self.cave.has_stench(column,row)== True:
                return True
            else:
                return False
        else:
            tkinter.messagebox.showinfo("Errors", "The position has not been visited yet.")
            return False             

#---------------------------------------------------------------------------------------------------
    def observation_pits(self, observed_locations):
        # observed_locations: a set of (column,row) pairs which have been visited
        # This function returns a dict which contains a set of var:val pairs indicating whether or not the visited
        # rooms have pits or not, var is a variable name representing a location and val is a truth value,
        # e.g. {'(1,2)':False, '(2,3)':False}.
        # Since the visited rooms must have no pit/wumpus, the truth value must be false.
        
        known_PW = {} # A dictionary, each element is a pair of variable name and truth value, var:val,
                      # var is the variable name representing a room, val is a truth value. 

        # for each visited room, each_v is a pair of column and row, each_v =(column,row)             
        for each_v in observed_locations:
            if each_v in self.visited_rooms:
                known_PW['(' + str(each_v[0]) +',' + str(each_v[1])+ ')' ] = False # add ('(column,row)': False) to known_PW
                                                                                    # meaning that room each_v does not have pit/wumpus
            else: tkinter.messagebox.showinfo("Errors", "The position has not been visited yet.")
        return known_PW

#---------------------------------------------------------------------------------------------------
    def observation_breeze_stench(self, observed_locations):
        # observed_locations: a set of (column,row) pairs which have been visited 
        # This function returns a dict which contains a set of var:val pairs indicating whether or not the visited
        # rooms have breeze/stench or not, var is a variable name representing a location and val is a truth value,
        # e.g. {'(1,2)':True, '(2,3)':False}.
        
        known_BS = {} # A dictionary, each element is a pair of variable name and truth value, var:val,
                      # the truth value represents whether the room has 'breeze' or 'stench'
                      
        # for each visited room, each_v is a pair of column and row, each_v =(column,row) 
        for each_v in observed_locations:
            if self.has_breeze(each_v[0], each_v[1])== True or self.has_stench(each_v[0], each_v[1]) == True:
                known_BS['(' + str(each_v[0]) +',' + str(each_v[1])+ ')' ] = True # if each_v has 'breeze' or 'stench', assign true
            else: known_BS['(' + str(each_v[0]) +',' + str(each_v[1])+ ')' ] = False # otherwise, false
        return known_BS


#---------------------------------------------------------------------------------------------------
    def consistent(self, known_BS, event):
        # known_BS: a dictionary containing the visited rooms with corresponding truth value for breeze/stench.
        #           Each element in known_BS is a pair of variable name and truth value, var:val, e.g. {'(1,2)':True, '(2,3)':False}.
        # event: a dictionary containing all rooms each with an instantiated truth value for pit/wumpus.
        #        Each element in event is a pair of variable name and truth value, var:val, e.g. {'(1,2)':True, '(2,3)':False}.
        # This function is to check if the truth values in known_BS are consistent with the values in the event.  
        # If any of the following conditions is not satisfied, return 0 meaning that known_BS is not consistent with event,
        # otherwise return 1 meaning that known_BS is consistent with event.
        #    1. If a room known_BS['(x,y)'] has no breeze/stench (i.e., its value is false), its surrounding rooms
        #       should not contain pit/wumpus.
        #    2. If a room has breeze/stench, its surrounding rooms must have at least one room which contains pit/wumpus.
        #
        
        # Check each of the rooms in known BS
        for var in list(known_BS.keys()):  
            col,ro = int(var[1]), int(var[3])
            if known_BS[var] == False: # if (col,ro) has no breeze but one of its neighbour has pit/wumpus, return 0
                if self.surrounding_contain_pits(col,ro, event) == True: 
                    return 0
            if known_BS[var] == True: # if (col,ro) has breeze but its neighours don't have pit/wumpus, return 0
                if self.surrounding_contain_pits(col,ro, event) == False:
                    return 0
        return 1
#---------------------------------------------------------------------------------------------------                
    def surrounding_contain_pits(self, column, row, event):
        # Check if the surrounding rooms of a room at (column,row) contain pit/wumpus.
        # Return True if exists at least one pit in the surrounding rooms of (column,row), 
        # return False if there is no any pit/wumpus in the surrounding rooms of (column,row).
        
        surrounding = self.cave.getsurrounding(column,row)
        for (col, ro) in surrounding: # each element is a pair of (column, row)
            var_name = '(' + str(col)+',' + str(ro)+ ')' # make up a PW variable name which is a string: '(col,ro)'
            if var_name in list(event.keys()) and event[var_name]==True: # only check the rooms which are in event
                return True # there exist a neighbour cell which has a pit/wumpus
        return False # there is no any pit/wumpus in surrounding locations

#---------------------------------------------------------------------------------------------------                
    def check_safety(self, column, row):
        # type: (object, object) -> object
        '''Using the method pl_resolution() from logic.py to determine the safety of room (column,row).
            Return True if there is no wumpus and no pit in it.
            Return false when there might be wumpus or pit in it.'''
        
        _wumpus_expr = expr("~W%d%d"%(column,row))
        _pit_expr = expr("~P%d%d"%(column,row))
       
        return pl_resolution(self.kb,_pit_expr) and pl_resolution(self.kb,_wumpus_expr)
           
#---------------------------------------------------------------------------------------------------

    ## This method is used by the logic based agent to update its knowledge base
    def kb_add(self,x,y):
        ''' Update the knowledge base by adding a new propositional expresstion
            into the konwledge base
            First, form the expression which is related to the location (x,y), x is column, y is row.
            then, add it into the knowledge base kb by using method tell() of PropKB'''

        expression=''
        # Generate an expression to represent breeze situation of the coordinate (x,y)
        if (x,y) in self.cave.breezeCoors: # (x,y) is a room with breeze
            ##if (x,y) is at bottom-left corner
            if(x,y)==(1,self.cave.HEIGHT):
                expression = expr("P%d%d | P%d%d"%(x,y-1,x+1,y)) # P(x, y-1) or P(x+1, y) has a pit
            ##if (x,y) is at top-left corner
            elif (x,y)==(1,1):
                expression = expr("P%d%d | P%d%d"%(x,y+1,x+1,y))
            ##if (x,y) is at top-right corner
            elif (x,y)==(self.cave.WIDTH,1):
                expression = expr("P%d%d | P%d%d"%(x-1,y,x,y+1))
            ##if (x,y) is at bottom-right corner
            elif (x,y)==(self.cave.WIDTH,self.cave.HEIGHT):
                expression = expr("P%d%d | P%d%d"%(x-1,y,x,y-1))
            ##if (x,y) is at top side(except the corners)
            elif x==1:
                expression = expr("P%d%d | P%d%d | P%d%d"%(x+1,y,x,y+1,x,y-1))
            ##if (x,y) is at bottom side(except the corners)
            elif x==self.cave.WIDTH:
                expression = expr("P%d%d | P%d%d | P%d%d"%(x,y+1,x,y-1,x-1,y))
            ##if (x,y) is at left side(except the corners)
            elif y==1:
                expression = expr("P%d%d | P%d%d | P%d%d"%(x+1,y,x,y+1,x-1,y))
            ##if (x,y) is at right side(except the corners)
            elif y ==self.cave.HEIGHT:
                expression = expr("P%d%d | P%d%d | P%d%d"%(x+1,y,x-1,y,x,y-1))
            else:
                expression = expr("P%d%d | P%d%d | P%d%d | P%d%d"%(x+1,y,x-1,y,x,y+1,x,y-1))
        else:
            # (x, y) is a room without breeze
            if(x,y)==(1,self.cave.HEIGHT): 
                expression = expr("~P%d%d & ~P%d%d"%(x,y-1,x+1,y))
            elif (x,y)==(1,1):
                expression = expr("~P%d%d & ~P%d%d"%(x,y+1,x+1,y))
            elif (x,y)==(self.cave.WIDTH,1):
                expression = expr("~P%d%d & ~P%d%d"%(x-1,y,x,y+1))
            elif (x,y)==(self.cave.WIDTH,self.cave.HEIGHT):
                expression = expr("~P%d%d & ~P%d%d"%(x-1,y,x,y-1))
            elif x==1:
                expression = expr("~P%d%d & ~P%d%d & ~P%d%d"%(x+1,y,x,y+1,x,y-1))
            elif x==self.cave.WIDTH:
                expression = expr("~P%d%d & ~P%d%d & ~P%d%d"%(x,y+1,x,y-1,x-1,y))
            elif y==1:
                expression = expr("~P%d%d & ~P%d%d & ~P%d%d"%(x+1,y,x,y+1,x-1,y))
            elif y ==self.cave.HEIGHT:
                expression = expr("~P%d%d & ~P%d%d & ~P%d%d"%(x+1,y,x-1,y,x,y-1))
            else:
                expression =expr("~P%d%d & ~P%d%d & ~P%d%d & ~P%d%d"%(x+1,y,x-1,y,x,y+1,x,y-1))
        self.kb.tell(expr(expression)) 

        # Generate an expression to represent stench situation of the coordinate (x,y)
        if (x,y) in self.cave.stenchCoors: # (x, y) is a cell with stench
            if(x,y)==(1,self.cave.HEIGHT):
                expression = expr("W%d%d | W%d%d"%(x,y-1,x+1,y))
            elif (x,y)==(1,1):
                expression = expr("W%d%d | W%d%d"%(x,y+1,x+1,y))
            elif (x,y)==(self.cave.WIDTH,1):
                expression = expr("W%d%d | W%d%d"%(x-1,y,x,y+1))
            elif (x,y)==(self.cave.WIDTH,self.cave.HEIGHT):
                expression = expr("W%d%d | W%d%d"%(x-1,y,x,y-1))
            elif x==1:
                expression = expr("W%d%d | W%d%d | W%d%d"%(x+1,y,x,y+1,x,y-1))
            elif x==self.cave.WIDTH:
                expression = expr("W%d%d | W%d%d | W%d%d"%(x,y+1,x,y-1,x-1,y))
            elif y==1:
                expression = expr("W%d%d | W%d%d | W%d%d"%(x+1,y,x,y+1,x-1,y))
            elif y ==self.cave.HEIGHT:
                expression = expr("W%d%d | W%d%d | W%d%d"%(x+1,y,x-1,y,x,y-1))
            else:
                expression = expr("W%d%d | W%d%d | W%d%d | W%d%d"%(x+1,y,x-1,y,x,y+1,x,y-1))
        else:
            # (x, y) is a cell without stench 
            if(x,y)==(1,self.cave.HEIGHT):
                expression = expr("~W%d%d & ~W%d%d"%(x,y-1,x+1,y))
            elif (x,y)==(1,1):
                expression = expr("~W%d%d & ~W%d%d"%(x,y+1,x+1,y))
            elif (x,y)==(self.cave.WIDTH,1):
                expression = expr("~W%d%d & ~W%d%d"%(x-1,y,x,y+1))
            elif (x,y)==(self.cave.WIDTH,self.cave.HEIGHT):
                expression = expr("~W%d%d & ~W%d%d"%(x-1,y,x,y-1))
            elif x==1:
                expression = expr("~W%d%d & ~W%d%d & ~W%d%d"%(x+1,y,x,y+1,x,y-1))
            elif x==self.cave.WIDTH:
                expression = expr("~W%d%d & ~W%d%d & ~W%d%d"%(x,y+1,x,y-1,x-1,y))
            elif y==1:
                expression = expr("~W%d%d & ~W%d%d & ~W%d%d"%(x+1,y,x,y+1,x-1,y))
            elif y ==self.cave.HEIGHT:
                expression = expr("~W%d%d & ~W%d%d & ~W%d%d"%(x+1,y,x-1,y,x,y-1))
            else:
                expression = expr("~W%d%d & ~W%d%d & ~W%d%d & ~W%d%d"%(x+1,y,x-1,y,x,y+1,x,y-1))
        self.kb.tell(expr(expression))
        
# End of class Robot
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#___________________________________________________________________________________________________


class Cave():
    '''This class is to define a 2D plane for representing the 2D cave environment.
       Each room or cell on the plane represents a room in the cave, which is indexed by
       a pair of coordinates (x,y), where x are y are not pixel coordinates, x is the index
       of columns and y is the index of rows for this room.
       The coordinates of pits, the wumpus, and the gold are all randomly generated unless you
       have explicitly chosen a fixed board.'''
    
#   Instance variables
#   ----------------------------------------------------------------------------------------------------
#   WIDTH = number of columns of the cave
#   HEIGHT = number of rows of the cave 
#   number_of_pit = number of pits in the cave
#   rooms = total number of rooms in the cave
#   _goldCoor = a pair of column and row of the gold. It is protected, supposed not be accessed from other classes except for GUI which is a subclass of Cave.
#   _wumpusCoor = a pair of column and row of the wumpu. It is protected, supposed not be accessed from other classes except for GUI which is a subclass of Cave.
#   _pitCoors = a set of coordinate pairs of pits. It is protected, supposed not be accessed from other classes except for GUI which is a subclass of Cave.
#   breezeCoors = a set of coordinate pairs of the positions which have breezes
#   stenchCoors = a set of coordinate pairs of the positions which have stenchs
#   
    
    def __init__(self,width,height,number_of_pits, *arg):        
        # Set up the size of the plane and the number of pits
        self.WIDTH=width   
        self.HEIGHT=height  
        self.number_of_pit = number_of_pits
        self.rooms = self.WIDTH*self.HEIGHT  # number of rooms in the cave environment

        # Each room in the cave is specified by a pair of coordinates (x, y), x is columm, y is row.
        
        # pits or wumpus are not deployed in the following three specific rooms. 
        #   (1,self.HEIGHT) is the first room at the bottom row,
        #   (2,self.HEIGHT) is the second room at the bottom row,
        #   (1,self.HEIGHT-1) is the first room at the second bottom row
        # The reason is that, when (2,self.HEIGHT) or (1,self.HEIGHT-1) contains a pit or the wumpus, 
        # the room (1,self.HEIGHT) will have breeze or stench. In this case, the logic based robot will never move.
        self.used_rooms =[(1,self.HEIGHT),(2,self.HEIGHT),(1,self.HEIGHT-1)]

        # Deploy the wumpus. For this implementation, only one wumpus
        if len(arg) == 0: # if arg is empty, it must be random board
            #self._wumpusCoor = (4,3)
            self._wumpusCoor = (randint(1, self.WIDTH), randint(1, self.HEIGHT))
            while self._wumpusCoor in self.used_rooms:
                #self._wumpusCoor = (4,3)
                self._wumpusCoor = (randint(1, self.WIDTH), randint(1, self.HEIGHT))
            self.used_rooms.append(self._wumpusCoor)
        else: # if arg is not empty, it must be fixed board
            self._wumpusCoor = (arg[1],arg[2])
            self.used_rooms.append(self._wumpusCoor)

        # Deploy pits.
        self._pitCoors=set()

        if len(arg) == 0:# if arg is empty, it must be a random board
            for i in range(0,self.number_of_pit): 
                '''if i == 0:
                    pit = (2,2)
                else:
                    pit = (3,4)'''
                pit =(randint(1,self.WIDTH),randint(1,self.HEIGHT))
                # Make sure the coordinate has not been occupied.
                while pit in self.used_rooms:
                    '''if i == 0:
                        pit = (2, 2)
                    else:
                        pit = (3, 4)'''
                    pit =(randint(1,self.WIDTH),randint(1,self.HEIGHT))
                self._pitCoors.add(pit)
                self.used_rooms.append(pit)
        else: # if arg is not empty, it must be a fixed board, add only one pit
            self._pitCoors.add((arg[3],arg[4]))
            self.used_rooms.append((arg[3],arg[4]))

        # Create a set of coordinates of 'breeze rooms' based on the positions of pits
        self.breezeCoors=set()
        # Check four rooms surrounding the room occupied by a pit
        for pit in self._pitCoors:
            if self.in_range(pit[0]+1,pit[1]):
                self.breezeCoors.add((pit[0]+1,pit[1]))
            if self.in_range(pit[0]-1,pit[1]):
                self.breezeCoors.add((pit[0]-1,pit[1]))
            if self.in_range(pit[0],pit[1]+1):
                self.breezeCoors.add((pit[0],pit[1]+1))
            if self.in_range(pit[0],pit[1]-1):
                self.breezeCoors.add((pit[0],pit[1]-1))

        # Create a set of coordinates of 'stench rooms' based on the position of wumpus
        self.stenchCoors = set()
        # Check four rooms around the room occupied by wumpus
        if self.in_range(self._wumpusCoor[0]+1,self._wumpusCoor[1]):
            self.stenchCoors.add((self._wumpusCoor[0]+1,self._wumpusCoor[1]))
        if self.in_range(self._wumpusCoor[0]-1,self._wumpusCoor[1]):
            self.stenchCoors.add((self._wumpusCoor[0]-1,self._wumpusCoor[1]))
        if self.in_range(self._wumpusCoor[0],self._wumpusCoor[1]+1):
            self.stenchCoors.add((self._wumpusCoor[0],self._wumpusCoor[1]+1))
        if self.in_range(self._wumpusCoor[0],self._wumpusCoor[1]-1):
            self.stenchCoors.add((self._wumpusCoor[0],self._wumpusCoor[1]-1))

        # Deploy the gold. For this implementation, only one piece of gold
        if len(arg) == 0:# if arg is empty, it must be random board
            self._goldCoor = (randint(1,self.WIDTH),randint(1,self.HEIGHT))
            # Make sure the coordinate has not been occupied.
            while self._goldCoor in self.used_rooms :
                self._goldCoor = (randint(1,self.WIDTH),randint(1,self.HEIGHT))
            # Add the position into used_rooms, meaning this position can't be used any more
            self.used_rooms.append(self._goldCoor)
        else: # if arg is not empty, it must be fixed board, add the gold
            self._goldCoor = (arg[5],arg[6])
            self.used_rooms.append((arg[5],arg[6]))

        # Remove the gold position from breezeCoors, make the room available to the robot
        if self._goldCoor in self.breezeCoors:
            self.breezeCoors.remove(self._goldCoor)
        # Remove the gold position from stenchCoors, make the room available to the robot
        if self._goldCoor in self.stenchCoors:
            self.stenchCoors.remove(self._goldCoor)

#---------------------------------------------------------------------------------------------------
    # Check if the coordinate(column,row) is within the plane
    def in_range(self,column, row):
        if column in range(1,self.WIDTH+1) and row in range(1,self.HEIGHT+1):
            return True
        else:
            return False
#---------------------------------------------------------------------------------------------------
    # Return valid adjacent rooms of (column,row)
    # "Valid rooms' refers to rooms which are within the plane
    # Return a list of 2-tuples, each tuple is a pair of (column,row)
    def getsurrounding(self, column, row):
        rooms=[]
        if self.in_range(column+1,row):
            rooms.append((column+1,row))
        if self.in_range(column-1,row):
            rooms.append((column-1,row))
        if self.in_range(column,row+1):
            rooms.append((column,row+1))
        if self.in_range(column,row-1):
            rooms.append((column,row-1))
        return rooms

#---------------------------------------------------------------------------------------------------
    # Return true if the room (column,row) contains breeze, otherwise return false
    def has_breeze(self,column,row):
        if (column,row) in self.breezeCoors:
            return True
        else:
            return False

#---------------------------------------------------------------------------------------------------
    # Return true if the room (column,row) contains stench, otherwise return false
    def has_stench(self,column,row):
        if (column,row) in self.stenchCoors:
            return True
        else:
            return False

# End of class Cave
#___________________________________________________________________________________________________________________________
#___________________________________________________________________________________________________________________________
#___________________________________________________________________________________________________________________________
#___________________________________________________________________________________________________________________________


class GUI(Cave):

    """GUI class to display the cave and the movements of the robot"""

    def __init__(self,parent,cave,robot):
        self.parent = parent # a Tk GUI
        self.cave = cave # the cave, i.e., the environment
        self.robot = robot # the agent
        self.WIDTH = cave.WIDTH # number of columns in the cave
        self.HEIGHT = cave.HEIGHT # number of rows in the cave

        ## Size of the environment which is a square
        self.canvas_height = board_height
        self.canvas_width = board_width
        self.length_of_side=600//(max(self.WIDTH,self.HEIGHT)+2) # length of each room

        ###Read all the pictures and resize them to fit the environment
        img=Image.open("IFN680_AIMA/images/gold.gif")
        self.image_gold=img.resize((self.length_of_side,self.length_of_side))
        self.gold_img=ImageTk.PhotoImage(self.image_gold)
        img=Image.open("IFN680_AIMA/images/visited.gif")
        self.image_visited=img.resize((self.length_of_side,self.length_of_side))
        self.visited_img=ImageTk.PhotoImage(self.image_visited)
        img=Image.open("IFN680_AIMA/images/blank.gif")
        self.image_blank=img.resize((self.length_of_side,self.length_of_side))
        self.blank_img=ImageTk.PhotoImage(self.image_blank)
        img=Image.open("IFN680_AIMA/images/wall.gif")
        self.image_wall=img.resize((self.length_of_side,self.length_of_side))
        self.wall_img=ImageTk.PhotoImage(self.image_wall)
        img=Image.open("IFN680_AIMA/images/robot.gif")
        self.image_robot=img.resize((self.length_of_side,self.length_of_side))
        self.robot_img=ImageTk.PhotoImage(self.image_robot)
        img=Image.open("IFN680_AIMA/images/wumpus.gif")
        self.image_wumpus=img.resize((self.length_of_side,self.length_of_side))
        self.wumpus_img=ImageTk.PhotoImage(self.image_wumpus)
        img=Image.open("IFN680_AIMA/images/pit.gif")
        self.image_pit=img.resize((self.length_of_side,self.length_of_side))
        self.pit_img=ImageTk.PhotoImage(self.image_pit)

        ########## Left Widgets ##########
        # Create game setting Frame
        self.game_setting = Frame(parent, borderwidth=2,relief=RIDGE)
        self.game_setting.grid(row = 0, column = 0)
        # setting frame title
        Label(self.game_setting,text = "Game Setting", font = ('Arial', 14, 'bold')).\
              grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5)

        # Let user choose the agent type: logic-based or probability-based
        Label(self.game_setting, text = 'Choose Agent Type: ', font = ('Arial', 10)).\
            grid(row = 1, column = 0,sticky = 'E', padx = 5, pady = 5)
        self.agent_type = Combobox(self.game_setting, text = "Agent Types",  \
                          state='readonly', font = ('Courier', 10), justify = LEFT)
        # Add the agent types
        self.agent_type['values'] = ('Probability based agent', 'Logic based agent')
        # Set the current position
        self.agent_type.current(0)
        # Add it to the setting panel
        self.agent_type.grid(row = 1, column = 1, sticky = W,padx = 5, pady = 5)

        # Add probability threshold, maximum probability of having a pit in a room
        Label(self.game_setting,text="Set the maximum probability of containing pits:",font = ('Arial', 10))\
                                          .grid(row = 2, column = 0,padx = 5, pady = 5)

        self.max_prob = Spinbox(self.game_setting, from_=0,to =1, increment=0.1)
        self.max_prob.grid(row = 2, column = 1, sticky = W,padx = 5, pady = 5)

        # Create result Frame
        self.result = Frame(self.game_setting,  borderwidth=2,relief=RIDGE)
        self.result.grid(row = 4, column = 0, columnspan = 2)
        # Result frame title
        Label(self.result,text = "Result", font = ('Arial', 14, 'bold')).\
              grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5)

        # single move numbers
        self.single_moves = Label(self.result,text="Number of moves:",font = ('Arial', 10))\
                                          .grid(row = 1, column = 0,padx = 3, pady = 3)
        self.s_move_num = StringVar() # single move numbers
        self.single_moves_num = Label(self.result,text="   ", textvariable=self.s_move_num,\
                                     font = ('Arial', 10), width = 10)
        self.single_moves_num .grid(row = 1, column = 1,padx = 3, pady = 3)

        # single run success
        self.single_success = Label(self.result,text="Success/failure:",font = ('Arial', 10))\
                                          .grid(row = 2, column = 0,padx = 3, pady = 3)
        self.s_success = StringVar() # single run result
        self.single_success = Label(self.result,text="   ", textvariable=self.s_success,\
                                     font = ('Arial', 10), width = 10)
        self.single_success .grid(row = 2, column = 1,padx = 3, pady = 3)

        # Create buttons to start the game
        self.buttons=Frame(self.game_setting, borderwidth=2,relief=RIDGE)
        self.buttons.grid(row=3, column = 0, columnspan = 2)
        Label(self.buttons,text = "Play", font = ('Arial', 14, 'bold')).\
              grid(row = 0, column = 0, columnspan = 3, padx = 5, pady = 5)
        self.button_move=Button(self.buttons,text="Start Game",command=self.start)
        self.button_move.grid(row=1, column=0)
        self.button_newgame=Button(self.buttons,text=" Replay Game ",command=self.refresh_game)
        self.button_newgame.grid(row=1, column=1)
        self.button_newgame=Button(self.buttons,text=" New Game ",command=self.start_newgame)
        self.button_newgame.grid(row=1, column=2)


        ########## Right Widgets ##########
        ##Create the environment board
        self.canvas=Canvas(parent,width=self.canvas_width,height=self.canvas_height)
        self.createGrid()
        self.canvas.grid(row = 0, column = 1, rowspan=2)

        parent.title("The Wumpus World")

#---------------------------------------------------------------------------------------------------
    ## This method is to create grids and deploy pits, the wumpus, the gold, and the robot depending on
    ## the current configuration
    def createGrid(self):
        for i in range(0,self.WIDTH+2):
            for j in range(0,self.HEIGHT+2):
                if (i,j)==self.cave._wumpusCoor:
                    self.canvas.create_image(self.length_of_side*i,self.length_of_side*j,anchor=NW,image=self.wumpus_img)
                elif (i,j) in self.cave._pitCoors:
                    self.canvas.create_image(self.length_of_side*i,self.length_of_side*j,anchor=NW,image=self.pit_img)
                elif (i,j)==self.robot.current_position:
                    self.canvas.create_image(self.length_of_side*i,self.length_of_side*j,anchor=NW,image=self.robot_img)
                elif i ==0 or i==(self.WIDTH+1) or j ==0 or j==(self.HEIGHT+1):
                    self.canvas.create_image(self.length_of_side*i,self.length_of_side*j,anchor=NW,image=self.wall_img)
                elif (i,j)in self.robot.visited_rooms:
                    self.canvas.create_image(self.length_of_side*i,self.length_of_side*j,anchor=NW,image=self.visited_img)
                elif (i,j)==self.cave._goldCoor:
                    self.canvas.create_image(self.length_of_side*i,self.length_of_side*j,anchor=NW,image=self.gold_img)
                else:
                    self.canvas.create_image(self.length_of_side*i,self.length_of_side*j,anchor=NW,image=self.blank_img)

#---------------------------------------------------------------------------------------------------
    ## This method is invoked by clicking on the "Start Game" button on the board GUI.
    ## Once started, the robot will move from one room to another
    ## until the robot finds the gold or died, or there is no more safe rooms to be explored
    def start(self):
        self.button_move.configure(state = DISABLED)
        if self.robot.gameover == False:
            self.GUI_move()
            if self.robot.current_position == self.cave._goldCoor:
                ## Get the number of moves and set into the result frame
                self.s_move_num.set(str(self.robot.num_moves))
                self.s_success.set('You won!')
                tkinter.messagebox.showinfo("Congrats","You have found the gold and you won!")
            else:##recursion after 100 millisecond, control moving speed
                # self.canvas.after(100,self.start) ###the speed can be controlled, make a choice in the main GUI to set up the speed
                self.canvas.after(500,self.start)
        else:
            if self.robot.dead == True:
                ## Get the number of moves and set into the result frame
                self.s_move_num.set(str(self.robot.num_moves))

                ## Get the result and set into the result frame
                self.s_success.set('You dead!')
                tkinter.messagebox.showinfo("Game over","You dead!")
            else:
                ## Get the number of moves and set into the result frame
                self.s_move_num.set(str(self.robot.num_moves-1))
                ## Get the result and set into the result frame
                self.s_success.set('No rooms!')
                tkinter.messagebox.showinfo("Game over","No available rooms to explore, fail!")

#---------------------------------------------------------------------------------------------------
    ## Make one move to a new room
    def GUI_move(self):
        # Get the agent type chosen by the user
        agent_type = self.agent_type.current()
        # print(agent_type)
        # Get the maximum probability threshold
        try:
            max_prob = float(self.max_prob.get())
        except ValueError as e:
            print(e)

        # Call method step() of Robot object robot to find a new room and move the robot to that new room
        # (column,row) is the new room that the robot has just moved in
        (column,row) = self.robot.step(agent_type, max_prob)

        ##if moving to the room with gold
        if (column,row)==self.cave._goldCoor:
            self.robot.gold_collected = True
        ##if moving to the room with Wumpus
        if (column,row)==self.cave._wumpusCoor:
            self.robot.dead = True
        ##if moving to the room with a pit
        if (column,row) in self.cave._pitCoors:
            self.robot.dead = True

        # Refresh the board
        self.createGrid()
        self.canvas.grid(row = 0, column = 1)
#---------------------------------------------------------------------------------------------------
    ## Start a new game
    def start_newgame(self):
        # self.parent.destroy()
        # main_GUI=Tk()
        # newGame(main_GUI, self.WIDTH,self.HEIGHT,self.cave.number_of_pit)
        self.cave = Cave(self.WIDTH,self.HEIGHT,self.cave.number_of_pit)
        self.robot = Robot(self.cave)
        self.clear_canvas()       

    ## refresh the game to compare logic and prob
    def refresh_game(self):
        # cave = self.cave
        self.robot = Robot(self.cave)
        self.clear_canvas()


    ##Create the environment board
    def clear_canvas(self):
        self.canvas=Canvas(self.parent,width=self.canvas_width,height=self.canvas_height)
        self.createGrid()
        self.canvas.grid(row = 0, column = 1, rowspan=2)
        self.button_move.configure(state = NORMAL)

# End of class GUI
#___________________________________________________________________________________________________________________________
#___________________________________________________________________________________________________________________________
#___________________________________________________________________________________________________________________________

## Start a new game
def newGame(main_GUI, number_of_columns,number_of_rows,number_of_pits):
    # Create an object of Cave to represent the cave environment
    cave  = Cave(number_of_columns,number_of_rows,number_of_pits)
    # Create an object of Robot to represent the robot trying to catch the gold
    robot = Robot(cave)

    # Create the GUI interface
    GUI(main_GUI,cave,robot)

#---------------------------------------------------------------------------------------------------
##
## The main program to start the game
##

if __name__ == '__main__':

    # Create the GUI interface for the game
    main_GUI=Tk()

    number_of_rows = 4
    number_of_columns = 4
    number_of_pits = 3

    ## Start a new game
    newGame(main_GUI,number_of_columns,number_of_rows,number_of_pits)

    main_GUI.title("The Wumpus World")
    main_GUI.mainloop()


# End of the program
#___________________________________________________________________________________________________________________________
#___________________________________________________________________________________________________________________________
#___________________________________________________________________________________________________________________________



