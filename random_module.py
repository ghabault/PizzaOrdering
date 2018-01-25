import numpy as np
from datetime import datetime, timedelta

def updateDictInList(source_list, name):
    for element in source_list:
        if element['name'] == name:
            element['amount'] +=1
            return True
    return False

def generateDate(start_datetime, date_range, hour_distribution, hour_probability, min_range):
    day = np.random.choice(date_range)
    hour = np.random.choice(hour_distribution, p=hour_probability)
    minute = np.random.choice(min_range)
    return start_datetime + timedelta(days=day, hours=hour, minutes=minute)

def compareTimes(test_date, time_min, time_max):
    min_dt = datetime.strptime(time_min, "%H:%M")
    max_dt = datetime.strptime(time_max, "%H:%M")
    if test_date.time() < min_dt.time() or test_date.time() > max_dt.time():
        return True
    else:
        return False

def generatePhoneNumber():
    phone_number = [0,0,0,0,0,0,0,0,0,0,0]
    for i in range(1,len(phone_number)):
        if i == 1:
            phone_number[i] = np.random.choice(range(1,10))
        else:
            phone_number[i] = np.random.choice(range(10))
    phone_str = ""
    for i in range(len(phone_number)):
        if i == 2 or i == 6:
            phone_str += "{}-".format(phone_number[i])
        else:
            phone_str += "{}".format(phone_number[i])
    return phone_str
