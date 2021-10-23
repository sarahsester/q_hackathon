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
min_teachers = schooldata["min_number_of_teachers"]
number_students = schooldata["student"]

w = 10
size_teacher = len(teacherdata)
size_school = len(schooldata)

# create matrix of teacher and school matching
teacher_school_x = [(i, j) for i in range(size_teacher) for j in range(size_school)]
#teacher_school_y = [(i, j) for i in range(size_teacher) for j in range(size_school)]
#teacher_school_z = [(i, j) for i in range(size_teacher) for j in range(size_school)]

# create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts("teacher_school", teacher_school_x, lowBound=0, upBound=1, cat=pulp.LpInteger)
#y = pulp.LpVariable.dicts("teacher_school", teacher_school_y, lowBound=0, upBound=1, cat=pulp.LpInteger)
#z = pulp.LpVariable.dicts("teacher_school", teacher_school_z, lowBound=0, upBound=1, cat=pulp.LpInteger)

assignment_model = pulp.LpProblem("Teacher_School_Model", pulp.LpMinimize)

assignment_model += pulp.lpSum(pulp.lpSum(distance[i, j] * x[i, j] +
                                          x[i, j] * abs(b[i]-sb[j]) * w +
                                          x[i, j] * abs(r[i]-sr[j]) * w #+
                                          #distance[i, j] * y[i, j] +
                                          #y[i, j] * abs(b[i]-sb[j]) * w +
                                          #y[i, j] * abs(r[i]-sr[j]) * w #+
                                          #distance[i, j] * z[i, j] +
                                          #z[i, j] * abs(b[i]-sb[j]) * w +
                                          #z[i, j] * abs(r[i]-sr[j]) * w
                                          for i in range(size_teacher)) for j in range(size_school))

# one school per teacher
for i in range(size_teacher):
    assignment_model += pulp.lpSum(x[i, j] for j in range(size_school)) == 1
#for i in range(size_teacher):
#    assignment_model += pulp.lpSum(y[i, j] for j in range(size_school)) == 1
# for i in range(size_teacher):
#     assignment_model += pulp.lpSum(z[i, j] for j in range(size_school)) == 1

# am schlechtesten behandelter Lehrer
for i in range(size_teacher):
    assignment_model += pulp.lpSum(x[i, j]*distance[i, j]
                                    for j in range(size_school)) <= 200
# + y[i, j]*distance[i, j] + z[i, j]*distance[i, j]
# max teachers
for j in range(size_school):
    assignment_model += pulp.lpSum(x[i, j] for i in range(size_teacher)) <= 50#number_students[j]/25
#for j in range(size_school):
#    assignment_model += pulp.lpSum(y[i, j] for i in range(size_teacher)) <= 50  # number_students[j]/25
# for j in range(size_school):
#     assignment_model += pulp.lpSum(z[i, j] for i in range(size_teacher)) <= 50  # number_students[j]/25

# min teachers
for j in range(size_school):
    assignment_model += pulp.lpSum(x[i, j] for i in range(size_teacher)) >= 10#min_teachers[j]
#for j in range(size_school):
#    assignment_model += pulp.lpSum(y[i, j] for i in range(size_teacher)) >= 10#min_teachers[j]
# for j in range(size_school):
#     assignment_model += pulp.lpSum(z[i, j] for i in range(size_teacher)) >= 10#min_teachers[j]

assignment_model.solve()

# Wieviele Lehrer an jeweilige Schulen geschickt werden
schulbelegung = []
for j in range(size_school):
    count = 0
    for i in range(size_teacher):
        if x[(i, j)].value() == 1.0:
            count = count + 1
    schulbelegung.append(count)

# Distanzen der einzelnen Lehrer (mit bzw ohne Präferenzen)
teacher_costs = []
for i in range(size_teacher):
    cost = 0
    for j in range(size_school):
         cost = cost + distance[i, j] * x[i, j].value() #+ x[i, j].value() * abs(b[i] - sb[j]) * w + x[i, j].value() * abs(r[i] - sr[j]) * w
    teacher_costs.append(cost)
print(teacher_costs)

print()
