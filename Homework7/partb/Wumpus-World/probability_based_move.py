#----- IFN680 Assignment 1 -----------------------------------------------#
#  The Wumpus World: a probability based agent
#         (the function next_room_prob)
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

from random import *
from IFN680_AIMA.logic import *
from IFN680_AIMA.utils import *
from IFN680_AIMA.probability import *
import tkinter.messagebox,time

#__________________________________________________________________________________________________________________________    
#___________________________________________________________________________________________________________________________    
#---------------------------------------------------------------------------------------------------------------------------
    #
    #  The following two functions are to be developed by you. They are functions in class Robot. If you need,
    #  you can add more functions in this file. In this case, you need to link these functions at the beginning
    #  of class Robot in the main program file the_wumpus_world.py.
    # 
#---------------------------------------------------------------------------------------------------
    #
    # For this assignment, we treat a pit and the wumpus equally. Therefore, each room has two states. One state is 'empty',
    # the other state is 'containing a pit or the wumpus'. Thus, we can use a Boolean variable to represent each room,
    # value 'True' means the room contains a pit/wumpus, value 'False' means the room is empty.
    #
    # For a cave with n columns and m rows, there are totally n*m rooms, i.e, we have n*m Boolean variables to represent the rooms.
    # A configuration of pits/wumpus in the cave is an event of these variables. Without restricting the number of pits, totally
    # there are 2 to the power of n*m possible configurations.
    # For example, for a cave with 2 columns and 2 rows, the cave has 4 rooms, there are 16 configurations, (True, True, True, True)
    # is one configuration meaning all rooms are occupied by a pit/wumpus, and (True, False, False, False) is another configuration
    # where only one room has a pit/wumpus, the other three rooms are empty.
    #
    # The function PitWumpus_probability_distribution() below is to construct the joint probability distribution of all possible
    # pits/wumpus configurations in a given cave. The two parameters, width and height, are the number of columns and the number
    # of rows in the cave, respectively. In this function, you can create an object of JointProbDist to store the joint probability
    # distribution. will be used by your function next_room_prob() below to calculate the required probabilities.
    #
    # This function will be called in the constructor of class Robot in the main program the_wumpus_world.py to construct the
    # joint probability distribution object. Your function next_room_prob() will need to use the joint probability distribution
    # to calculate the required conditional probabilities.
    #
    
def PitWumpus_probability_distribution(self, width, height):

    # Select rooms in the fringe only as the probability is independent of other rooms
    fringe = []
    fringe = list(self.available_rooms)
    known_BS = self.observation_breeze_stench(self.visited_rooms)
    known_PW = self.observation_pits(self.visited_rooms)
    print('available_rooms:',self.available_rooms)

    P = JointProbDist(fringe, { each:[T, F] for each in fringe })

    events = all_events_jpd(fringe, P, known_PW)
    # for each in events:
    #     prob = 1
    #     for (var, val) in list(each.items()):
    #         if val:
    #             prob *= .2
    #         else:
    #             prob *= .8
    #     P[each] = self.consistent(known_BS, each) * prob
        
    room_size = self.cave.WIDTH * self.cave.HEIGHT

    p_true = 0.2
    p_false = 1 - p_true
    for each in events:
        # prob = 1
        # for (var, val) in list(each.items()):
        #     if val:
        #         prob *= .2
        #     else:
        #         prob *= .8
        # P[each] = self.consistent(known_BS, each) * prob
        true_count = sum(map((True).__eq__, each.values()))
        P[each] = (p_true ** true_count) * (p_false ** (room_size - true_count))

    print('prob of other rooms:', P)

    return P


#---------------------------------------------------------------------------------------------------
    #
    #  For the function next_room_prob() below, the parameters, column and row, are the robot's
    #  current position (column,row) in the cave environment. This function is to find the next
    #  room for the robot to go. There are three cases:
    #
    #    1. Firstly, you may like to call the function check_safety() of class Robot to find a
    #       safe room. If there is a safe room, return the location (column,row) of the safe room.
    #    2. If there is no safe room, this function needs to choose a room whose probability of containing
    #       a pit/wumpus is lower than a pre-specified probability threshold, then return the location of
    #       that room.
    #    3. If the probabilities of all the available rooms are not lower than the pre-specified probability
    #       threshold, return (0,0).
    #
def next_room_prob(self, column, row):
    new_room = (0, 0)
    fringe = []
    # lowest_prob holds the temp value of the lowest probability a room has a pit/wumpus
    # at the end of the for loop, lowest_prob holds the value of the lowest probabilit a room has a pit/wumpus
    lowest_prob = 1
    fringe = list(self.available_rooms)
    # known_BS = self.observation_breeze_stench(self.visited_rooms)
    # known_PW = self.observation_pits(self.visited_rooms)
    for each_room in fringe:
        if self.check_safety(each_room[0], each_room[1]) == True:
            new_room = each_room
            break
        else:
            prob_each_room = enumerate_joint_ask(each_room, {}, self.PitWumpus_probability_distribution(self.cave.WIDTH,
                                                                                                        self.cave.HEIGHT))
            if prob_each_room.prob[True] < lowest_prob:
                lowest_prob = prob_each_room.prob[True]
                if lowest_prob <= self.max_pit_probability:
                    new_room = each_room
    return new_room







 
