from random import randint, random
from functools import reduce
from operator import add

def individual(length, min, max):
    'Create a member of the population.'
    return [randint(int(min), int(max)) for x in range(length)]


def population(count, length, min, max):
    """
        Create a number of individuals (i.e. a population).


        count: the number of individuals in the population
        length: the number of values per individual
        min: the minimum possible value in an individual's list of values
        max: the maximum possible value in an individual's list of values
        """
    return [individual(length, min, max) for x in range(count)]


def fitness(individual, target):
    """
        Determine the fitness of an individual. Higher is better.
        individual: the individual to evaluate
        target: the target number individuals are aiming for
        """
    nArray = [ num*num for num in individual]
    nSum = sum(nArray)
    return abs(target - nSum)


def grade(x, target):
    'Find average fitness for a population.'
    summed = reduce(add, (fitness(i, target) for i in x), 0)
    return summed / (len(x) * 1.0)

def evolve(pop, target, retain=0.2, random_select=0.05, mutate=0.01):
    graded = [(fitness(x, target), x) for x in pop]
    graded = [x[1] for x in sorted(graded)]
    retain_length = int(len(graded) * retain)
    parents = graded[:retain_length]
    # randomly add other individuals to
    # promote genetic diversity
    for individual in graded[retain_length:]:
        if random_select > random():
            parents.append(individual)
    # mutate some individuals
    for individual in parents:
        if mutate > random():
            pos_to_mutate = randint(0, len(individual) - 1)
    # this mutation is not ideal, because it
    # restricts the range of possible values,
    # but the function is unaware of the min/max
    # values used to create the individuals,
            individual[pos_to_mutate] = randint(min(individual), max(individual))
    # crossover parents to create children
    parents_length = len(parents)
    desired_length = len(pop) - parents_length
    children = []
    while len(children) < desired_length:
        male = randint(0, parents_length - 1)
        female = randint(0, parents_length - 1)
        if male != female:
            male = parents[male]
            female = parents[female]
            half = int(len(male) / 2)
            child = male[:half] + female[half:]
            children.append(child)
    parents.extend(children)
    return parents

def goal_state(N, X, P):
    """
        If there is a solution, return it. If not, return no solution.
        N: the length of solution list
        X: the target number individuals are aiming for
        P: the num of population
        """
    i_min = 0
    # control the max i to get the solution more precisely
    # for example, if set i_max as a const(e.g.100) with X=100 and N=2
    # the program may not assigned the population list without the solution
    if int(X**0.5) > N:
        i_max = X**0.5+1
    else:
        i_max = N
    p = population(P, N, i_min, i_max)
    fitness_history = [grade(P, X), ]
    for i in range(100):
        p = evolve(p, X)
        p_fitness = grade(p, X)
        fitness_history.append(p_fitness)
    return p[len(p)-1]


def main():
    while True:
        try:
            N = int(input("Please enter integer N(N>=2): "))
            X = int(input("Please enter integer X(X>=1): "))
            #population
            P = int(input("Please enter an integer of population size P: "))
            i_min = 0
            # control the max i to get the solution more precisely
            # for example, if set i_max as a const(e.g.100) with X=100 and N=2
            # the program may not assigned the population list without the solution
            if int(X ** 0.5) > N:
                i_max = X ** 0.5 + 1
            else:
                i_max = N
            p = population(P, N, i_min, i_max)
            fitness_history = [grade(p, X), ]

            for i in range(500):
                p = evolve(p, X)
                fit = grade(p, X)
                fitness_history.append(fit)

            print("Fitness History: ", fitness_history)

            print("Fitness History end result", )
            print("Result: ", p[len(p) - 1])
        except ValueError:
            print("Please input an positive integer!")

main()