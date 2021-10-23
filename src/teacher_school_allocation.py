from ortools.linear_solver import pywraplp
import pandas as pd
import numpy as np


def create_cost_matrix(distances, pref_big_school, pref_rural):
    cost_matrix = distances + 10 * pref_big_school + 10 * pref_rural
    return cost_matrix


def find_optimal_allocation(df_schools, distances, pref_big_school, pref_rural, number_teachers, number_schools):
    # Create cost matrix
    cost_matrix = create_cost_matrix(distances, pref_big_school, pref_rural)

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

    # Constraint 2: Each school is assigned to minimum x teachers.
    for s in range(number_schools):
        solver.Add(solver.Sum([x[t, s] for t in range(number_teachers)]) >= df_schools['min_number_of_teachers'][s])

    # Constraint 3: Each school is assigned to maximal x+20 teachers.
    for s in range(number_schools):
        solver.Add(
            solver.Sum([x[t, s] for t in range(number_teachers)]) <= df_schools['min_number_of_teachers'][s] + 20)

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

    df = pd.DataFrame(columns=['iteration', 'teacher', 'school', 'cost', 'dist'])

    # Save costs for further iterations
    costs_per_teacher = []

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f'Total cost = {solver.Objective().Value()}\n')
        for t in range(number_teachers):
            for s in range(number_schools):
                # Test if x[t,s] is 1 (with tolerance for floating point arithmetic).
                if x[t, s].solution_value() > 0.5:
                    print(f'Teacher {t} assigned to school {s}.  Cost={cost_matrix[t][s]}')
                    df = df.append({'iteration': 1, 'teacher': t, 'school': s, 'cost': cost_matrix[t][s],
                                    'dist': distances[t][s],
                                    'pref_school_size_unsatisfied': pref_big_school[t][s],
                                    'pref_urban_rural_unsatisfied': pref_rural[t][s]},
                                   ignore_index=True)
                    costs_per_teacher.append(cost_matrix[t][s])

    adapted_costs = cost_matrix * np.array(costs_per_teacher)[:, np.newaxis] / 10

    return df, adapted_costs


def find_optimal_allocation_it2(df_schools, distances, pref_big_school, pref_rural, number_teachers, number_schools,
                                adapted_cost_matrix):
    # Create cost matrix
    cost_matrix = create_cost_matrix(distances, pref_big_school, pref_rural)

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

    # Constraint 2: Each school is assigned to minimum x teachers.
    for s in range(number_schools):
        solver.Add(solver.Sum([x[t, s] for t in range(number_teachers)]) >= df_schools['min_number_of_teachers'][s])

    # Constraint 3: Each school is assigned to maximal x+20 teachers.
    for s in range(number_schools):
        solver.Add(
            solver.Sum([x[t, s] for t in range(number_teachers)]) <= df_schools['min_number_of_teachers'][s] + 20)

    # Constraint 4: Each teacher has a maximum cost of 100.
    for t in range(number_teachers):
        solver.Add(solver.Sum([cost_matrix[t][s] * x[t, s] for s in range(number_schools)]) <= 100)

    # Objective
    objective_terms = []
    for t in range(number_teachers):
        for s in range(number_schools):
            objective_terms.append(adapted_cost_matrix[t][s] * x[t, s])
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    status = solver.Solve()

    df = pd.DataFrame(columns=['iteration', 'teacher', 'school', 'cost', 'dist'])

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f'Total cost = {solver.Objective().Value()}\n')
        for t in range(number_teachers):
            for s in range(number_schools):
                # Test if x[t,s] is 1 (with tolerance for floating point arithmetic).
                if x[t, s].solution_value() > 0.5:
                    print(f'Teacher {t} assigned to school {s}.  Cost={cost_matrix[t][s]}')
                    df = df.append({'iteration': 2, 'teacher': t, 'school': s, 'cost': cost_matrix[t][s],
                                    'dist': distances[t][s],
                                    'pref_school_size_unsatisfied': pref_big_school[t][s],
                                    'pref_urban_rural_unsatisfied': pref_rural[t][s]},
                                   ignore_index=True)

    return df


if __name__ == '__main__':
    nb_of_teachers = 761
    nb_of_schools = 58

    # Get school data
    df_schools = pd.read_csv('../data/school_dataset.csv')

    # Get cost matrix
    distances = pd.read_pickle('../data/geopy_distance_matrix_Waldorfschule.pkl')
    # distances = np.random.rand(nb_of_teachers, nb_of_schools) * 200
    pref_big_school = pd.read_pickle(r'../data/preference_big_school_Waldorfschule.pkl')
    pref_rural = pd.read_pickle(r'../data/preference_rural_Waldorfschule.pkl')

    df, adapted_costs = find_optimal_allocation(df_schools, distances, pref_big_school, pref_rural,
                                                number_teachers=nb_of_teachers, number_schools=nb_of_schools)
    print(df)
    print(df.groupby(['school']).count()['teacher'])
    print(f'Average costs: {df["cost"].mean()}.')
    print(f'Teacher {df["cost"].argmin()} has minimum costs ({df["cost"].min()}).')
    print(f'Teacher {df["cost"].argmax()} has maximal costs ({df["cost"].max()}).')

    print(adapted_costs)

    df2 = find_optimal_allocation_it2(df_schools, distances, pref_big_school, pref_rural, number_teachers=nb_of_teachers,
                                      number_schools=nb_of_schools, adapted_cost_matrix=adapted_costs)
    print(df2)
    print(df2.groupby(['school']).count()['teacher'])
    print(f'Average costs: {df2["cost"].mean()}.')
    print(f'Teacher {df2["cost"].argmin()} has minimum costs ({df2["cost"].min()}).')
    print(f'Teacher {df2["cost"].argmax()} has maximal costs ({df2["cost"].max()}).')

    df_all = df.append(df2)
    df_all.to_csv('../data/results.csv', index=False)
