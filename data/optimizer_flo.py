import pulp
import pandas as pd
import pickle
with open('geopy_distance_matrix_Waldorfschule.pkl', 'rb') as f:
    distance = pickle.load(f)

schooldata = pd.read_csv(r'C:\Users\engel\PycharmProjects\q_hackathon\data\school_dataset.csv')
teacherdata = pd.read_csv(r'C:\Users\engel\PycharmProjects\q_hackathon\data\teachers.csv')
#schooldata = schooldata[schooldata["school_type"].isin(["Gymnasium", "Hauptschule", "Realschule"])]
schooldata = schooldata[schooldata["school_type"].isin(["Waldorfschule"])].reset_index()
#teacherdata = teacherdata[teacherdata["type_of_school"].isin(["Gymnasium", "Hauptschule", "Realschule"])]
teacherdata = teacherdata[teacherdata["type_of_school"].isin(["Waldorfschule"])].reset_index()

b = teacherdata["preference_big_school"]
r = teacherdata["preference_rural"]
sb = schooldata["is_big"]
sr = schooldata["is_rural"]
w = 10
size_teacher = len(teacherdata)
size_school = len(schooldata)

# create matrix of teacher and school matching
teacher_school = [(i, j) for i in range(size_teacher) for j in range(size_school)]

# create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts("teacher_school", teacher_school, lowBound=0, upBound=1, cat=pulp.LpInteger)

assignment_model = pulp.LpProblem("Teacher_School_Model", pulp.LpMinimize)

#assignment_model += pulp.lpSum(pulp.lpSum(distance[i, j] * x[i, j] + x[i, j] * abs(b[i]-sb[j])*w + x[i, j] * abs(r[i]-sr[j])*w
#                                          for i in range(size_teacher))
#                               for j in range(size_school))
assignment_model += pulp.lpSum(pulp.lpSum(distance[i, j] * x[i, j] +
                                          x[i, j] * abs(b[i]-sb[j]) * w +
                                          x[i, j] * abs(r[i]-sr[j])*w
                                          for i in range(size_teacher)) for j in range(size_school))

for i in range(size_teacher):
    assignment_model += pulp.lpSum(x[i, j] for j in range(size_school)) == 1

for i in range(size_teacher):
    assignment_model += pulp.lpSum(x[i, j]*distance[i, j] for j in range(size_school)) <= 100

for j in range(size_school):
    assignment_model += pulp.lpSum(x[i, j] for i in range(size_teacher)) <= 50

for j in range(size_school):
    assignment_model += pulp.lpSum(x[i, j] for i in range(size_teacher)) >= 10

assignment_model.solve()

#schulbelegung = []
#for j in range(size_school):
#    count = 0
#    for i in range(size_teacher):
#        if x[(i, j)].value() == 1.0:
#            count = count + 1
#    schulbelegung.append(count)


teacher_costs = []
for i in range(size_teacher):
    cost = 0
    for j in range(size_school):
         cost = cost + distance[i, j] * x[i, j].value() #+ x[i, j].value() * abs(b[i] - sb[j]) * w + x[i, j].value() * abs(r[i] - sr[j]) * w
    teacher_costs.append(cost)

print()
