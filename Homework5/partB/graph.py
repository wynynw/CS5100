# Import libraries
import aima.utils
import aima.planning
# Drive in romania
def romania():
    # Create a knowledge base
    knowledge_base = [
    aima.utils.expr("Connected(Bucharest,Pitesti)"),
    aima.utils.expr("Connected(Pitesti,Rimnicu)"),
    aima.utils.expr("Connected(Rimnicu,Sibiu)"),
    aima.utils.expr("Connected(Sibiu,Fagaras)"),
    aima.utils.expr("Connected(Fagaras,Bucharest)"),
    aima.utils.expr("Connected(Pitesti,Craiova)"),
    aima.utils.expr("Connected(Craiova,Rimnicu)")
    ]
    # Add rules to knowledge base
    knowledge_base.extend([
     aima.utils.expr("Connected(x,y) ==> Connected(y,x)"),
     aima.utils.expr("At(Sibiu)")
    ])
    # Create a drive action
    drive = aima.planning.Action('Drive(x, y)', precond='At(x) & Connected(x,y)', effect='At(y) & ~At(x)')
    # Create a goal
    goals = 'At(Bucharest)'
    # Graph plan solution
    problem = aima.planning.PlanningProblem(knowledge_base, goals, [drive])
    solution = aima.planning.GraphPlan(problem).execute()
    print("Romania: {0}".format(aima.planning.linearize(solution)))
    print()


# Tell python to run main method
if __name__ == "__main__":
    romania()