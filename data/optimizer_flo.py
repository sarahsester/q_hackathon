import pulp
import pandas as pd

schooldata = pd.read_csv(r'C:\Users\engel\PycharmProjects\q_hackathon\data\school_dataset.csv')
teacherdata = pd.read_csv(r'C:\Users\engel\PycharmProjects\q_hackathon\data\teachers.csv')
schooldata = schooldata[schooldata["school_type"] == "Waldorfschule"]
teacherdata = teacherdata[teacherdata["type_of_school"] == "Waldorfschule"]

distance = pd.DataFrame()

b = schooldata["is_big"]
r = schooldata["is_rural"]
sb = teacherdata["preference_big_school"]
sr = teacherdata["preference_rural"]
w = 5
size_teacher = len(schooldata)
size_school = len(teacherdata)

# create matrix of teacher and school matching
teacher_school = [(i, j) for i in range(size_teacher) for j in range(size_teacher)]

# create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts("teacher_school", teacher_school, lowBound=0, upBound=1, cat=pulp.LpInteger)

assignment_model = pulp.LpProblem("Teacher School Model", pulp.LpMinimize)

assignment_model += pulp.lpSum(pulp.lpSum(distance[i, j] * x[i, j] + x[i, j] * abs(b[i]-sb[j])*w + x[i, j] * abs(r[i]-sr[j])*w
                                          for i in range(size_teacher))
                               for j in range(size_school))

for i in range(size_teacher):
    assignment_model += pulp.lpSum(x[i, j] for j in range(size_school)) == 1

for i in range(size_teacher):
    assignment_model += pulp.lpSum(x[i, j]*distance[i, j] for j in range(size_school)) <= 100

for j in range(size_school):
    assignment_model += pulp.lpSum(x[i, j] for i in range(size_teacher)) <= schooldata["student"][j]/25

assignment_model.solve()
