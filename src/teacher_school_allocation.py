from ortools.linear_solver import pywraplp
import pandas as pd
import numpy as np


def create_cost_matrix(distances, pref_big_school, pref_rural):
    cost_matrix = distances + pref_big_school + pref_rural
    return cost_matrix


def find_optimal_allocation(cost_matrix, number_teachers, number_schools):
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # x[t,s] is an array of 0-1 variables, which will be 1 if teacher t is assigned to school s.
    x = {}
    for t in range(number_teachers):
        for s in range(number_schools):
            x[t, s] = solver.IntVar(0, 1, '')

    # Constraint 1: Each teacher is assigned to one school.
    for t in range(number_teachers):
        solver.Add(solver.Sum([x[t, s] for s in range(number_schools)]) == 1)

    # Constraint 2: Each school is assigned to minimum three teacher.
    for s in range(number_schools):
        solver.Add(solver.Sum([x[t, s] for t in range(number_teachers)]) >= 1)

    # Constraint 3: Each school is assigned to maximal 50 teachers.
    for s in range(number_schools):
        solver.Add(solver.Sum([x[t, s] for t in range(number_teachers)]) <= 200)

    # Constraint 4: Each teacher has a maximum cost of 100.
    for t in range(number_teachers):
        solver.Add(solver.Sum([cost_matrix[t][s] * x[t, s] for s in range(number_schools)]) <= 100)

    # Objective
    objective_terms = []
    for t in range(number_teachers):
        for s in range(number_schools):
            objective_terms.append(cost_matrix[t][s] * x[t, s])
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f'Total cost = {solver.Objective().Value()}\n')
        for t in range(number_teachers):
            for s in range(number_schools):
                # Test if x[t,s] is 1 (with tolerance for floating point arithmetic).
                if x[t, s].solution_value() > 0.5:
                    print(f'Teacher {t} assigned to school {s}.  Cost={cost_matrix[t][s]}')


if __name__ == '__main__':
    nb_of_teachers = 100
    nb_of_schools = 100

    # Get cost matrix
    #distances = pd.read_csv('../data/distances.csv')
    distances = np.random.rand(nb_of_teachers, nb_of_schools) * 200
    pref_big_school = pd.read_pickle(r'../data/preference_big_school.pkl')
    pref_rural = pd.read_pickle(r'../data/preference_rural.pkl')
    costs = create_cost_matrix(distances, pref_big_school[0:nb_of_teachers, 0:nb_of_schools], pref_rural[0:nb_of_teachers, 0:nb_of_schools])

    #print(costs)
    costs2 = [
        [90, 80, 75, 70],
        [35, 85, 55, 65],
        [125, 95, 90, 95],
        [45, 110, 95, 115],
        [50, 100, 90, 100],
    ]
    find_optimal_allocation(costs, number_teachers=nb_of_teachers, number_schools=nb_of_schools)
