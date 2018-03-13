import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

from collections import defaultdict

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False

        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def forwardChecking ( self ):
        for v in self.network.variables:
            if v.isAssigned():
                v_value = v.getValues()[0]
                # iterate through all neighbors of the recent assigned variable
                for i in self.network.getNeighborsOfVariable(v):
                    if i.isAssigned() and i.getAssignment()==v_value:
                        return False # contradiction! constraint is no longer consistent
                    else:
                        if v_value in i.domain.values:
                            self.trail.push( i )
                            # eliminate the assigned value from neighbors' domain
                            i.removeValueFromDomain(v_value)
                
                
        return True
    
    
    
    
    
    
    
    
    

    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def norvigCheck ( self ):        
        for v in self.network.variables:
            if v.isAssigned():
                v_value = v.getValues()[0]
                # iterate through all neighbors of the recent assigned variable
                for i in self.network.getNeighborsOfVariable(v):
                    if i.isAssigned() and i.getAssignment()==v_value:
                        return False # contradiction! constraint is no longer consistent
                    else:
                        if v_value in i.domain.values:
                            self.trail.push( i )
                            # eliminate the assigned value from neighbors' domain
                            i.removeValueFromDomain(v_value)
                            
                            if len(i.domain.values) == 1:
                                self.trail.push( i )
                                i.assignValue(i.domain.values[0])
        return True
    

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        # eliminate initial assigned values from their neighbors' domains
        if self.trail.trailStack == []:
            for i in self.network.variables:
                if i.isAssigned():
                    for j in self.network.getNeighborsOfVariable(i):
                        j.removeValueFromDomain(i.getValues()[0]) 
                        
        # first unassigned variable        
        temp = self.getfirstUnassignedVariable()
        
        if temp == None:
            return temp # equals None if everything is assined
        
        # iterate through all variables
        for i in self.network.variables:            
            if not (i.isAssigned()) and i.size() < temp.size():
                temp = i # update the variable with the smaller domain size
        
        return temp
                

    """
        Part 2 TODO: Implement the Degree Heuristic

        Return: The unassigned variable with the most unassigned neighbors
    """
    def getDegree ( self ):
        result = None
#        maxi = 3 * (self.gb.N - 1) - (self.gb.p - 1) - (self.gb.q - 1)
        max_deg = -1
        
        for i in self.network.variables:
            if not (i.isAssigned()):
                i_deg = 0
                for j in self.network.getNeighborsOfVariable(i):
                    if not j.isAssigned():
                        i_deg += 1
                if i_deg > max_deg:
                    max_deg = i_deg
                    result = i
        return result

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
        # eliminate initial assigned values from their neighbors' domains
        if self.trail.trailStack == []:
            for i in self.network.variables:
                if i.isAssigned():
                    for j in self.network.getNeighborsOfVariable(i):
                        j.removeValueFromDomain(i.getValues()[0]) 
                        
        # first unassigned variable        
        temp = self.getfirstUnassignedVariable()
        
        if temp == None:
            return temp # equals None if everything is assined
        
        # iterate through all variables
        for i in self.network.variables:            
            if not (i.isAssigned()) and i.size() < temp.size():
                temp = i # update the variable with the smaller domain size
        
        
        result = temp
        smallest_domain_size = result.size()
        max_deg = 0        
        for j in self.network.getNeighborsOfVariable(result):
            if not j.isAssigned():
                max_deg += 1
                
        for i in self.network.variables:
            if not (i.isAssigned()) and i.size() == smallest_domain_size and i!=result:
                i_deg = 0
                for j in self.network.getNeighborsOfVariable(i):
                    if not j.isAssigned():
                        i_deg += 1
                if i_deg > max_deg:
                    max_deg = i_deg
                    result = i

        return result
                

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):
        values = v.domain.values
        
        # dictionary of the frequency of all single value appears in the constraints
        frequent_dict = defaultdict(int)
        
        for var in self.network.getNeighborsOfVariable(v):
            for value in var.domain.values:
                frequent_dict[value] += 1
        # sort the values of input variable v by the frequency
        return sorted(values, key = (lambda x:frequent_dict[x]))
            

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)