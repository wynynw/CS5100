#___________________________________________________________________________________________________________________________    
#---------------------------------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------
    # This is a function in class Robot. It is used to find the next safe room for the robot to go.
    # It finds the safe room by using a propositional logic resolution method.
    # The parameters, column and row, are the robot's current position. If there is no
    # safe room available, return (0,0), otherwise return the column and row, (column,row), of the new room.
    #----------------------------------------------------------------------------------------------------------------------
#__________________________________________________________________________________________________________________________    

    
def next_room(self, column, row):
    new_room = (0,0)
    # Get surrounding rooms of the position (column,row), which are potential rooms to explore
    surroundings = self.cave.getsurrounding(column,row)
    # loop to see if there is any surrounding room that has not been visited and is safe to visit
    for each_s in surroundings:
        if each_s not in self.visited_rooms:
            if self.check_safety(each_s[0],each_s[1]): ## method check_safety() does a propositional-logic resolution reasoning to
                                                           ## determine whether moving to position each_s is safe or not
                new_room = each_s ## if it is safe, return this room, otherwise return (0,0)
                break
            
    return new_room 
