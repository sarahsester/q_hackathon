import requests
import json
import os
import numpy as np
import pandas as pd
import datetime

path_parent = os.path.dirname(os.getcwd())
data_path = os.path.join(path_parent, 'data')
df_school = pd.read_csv(os.path.join(data_path, 'school_dataset.csv'), encoding='utf-8', index_col = False)
df_teacher = pd.read_csv(os.path.join(data_path, 'teachers.csv'), encoding='utf-8', index_col = False)

distance_ar = np.zeros((df_school.shape[0], df_teacher.shape[0]))
#duration_ar = np.zeros((df_school.shape[0], df_teacher.shape[0]))


for i in range(df_school.shape[0]):
    lat_school = df_school['latitude'][i]
    long_school = df_school['longitude'][i]

    for j in range(df_teacher.shape[0]):
        lat_teacher = df_teacher['latitude'][j]
        long_teacher = df_teacher['longitude'][j]

        # call the OSMR API
        r = requests.get(f"http://router.project-osrm.org/route/v1/car/{long_school},{lat_school};{long_teacher},{lat_teacher}?overview=false""")

        # then you load the response using the json libray
        # by default you get only one alternative so you access 0-th element of the `routes`
        routes = json.loads(r.content)
        route_1 = routes.get("routes")[0]
        duration = str(datetime.timedelta(seconds=route_1["duration"]))
        distance = route_1['distance'] / 1000

        duration_ar[i][j] = (duration, distance)
        #distance_ar[i][j] = distance

        test =1