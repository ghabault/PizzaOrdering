import numpy as np
from datetime import datetime, timedelta
from order import *
from shapely.geometry import Polygon, Point

def generatedDists(source_list):
    order_dist = []
    delivery_dist = []
    for order in source_list:
        order_dist.append(order.date.hour)
        if order.delivery_date is not None:
            delivery_dist.append(order.delivery_date.hour)
    return {'order':order_dist, 'delivery':delivery_dist}

def updateDictInList(source_list, name):
    for element in source_list:
        if element['name'] == name:
            element['amount'] +=1
            return True
    return False

def generateDate(start_datetime, date_range, hour_distribution, hour_probability, min_range):
    result_dt = start_datetime + timedelta(days=-1)
    while result_dt < start_datetime:
        day = int(np.random.choice(date_range))
        hour = int(np.random.choice(hour_distribution, p=hour_probability))
        minute = int(np.random.choice(min_range))
        result_dt += timedelta(days=day+1)
        result_dt = result_dt.replace(hour=hour, minute=minute)
    return result_dt

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

def random_points_within(area, num_points):
    polygon = Polygon(area)
    min_x, min_y, max_x, max_y = polygon.bounds

    points = []

    while len(points) < num_points:
        random_point = Point([np.random.uniform(min_x, max_x), np.random.uniform(min_y, max_y)])
        if (random_point.within(polygon)):
            points.append([random_point.x, random_point.y])

    return points

def generateOrderList(date_start, date_end, names, order_params, delivery_params,
    position_limits):
    start_dt = datetime.strptime(date_start, "%Y-%m-%dT%H:%M")
    end_dt = datetime.strptime(date_start, "%Y-%m-%dT%H:%M")

    # Determine the delivery addresses
    generatedPositions = random_points_within(position_limits, order_params['num'])

    orders = []
    for i in range(order_params['num']):
        order = Order()
        # Choose a customer Name and phone number
        order.name = np.random.choice(names)
        order.phone = generatePhoneNumber()
        # Determine the delivery shop_address
        order.delivery_address = {'lat':generatedPositions[i][0], 'lon':generatedPositions[i][1]}
        # Determine the order date
        order.date = generateDate(start_dt, range(0,(end_dt-start_dt).days+1),
            order_params['dist'], order_params['prob'], range(0,60))

        # Determine if the delivery is asap or planned
        if compareTimes(order.date, "08:00", "22:00"):
            # Between 22:00 and 08:00 the chance for the delivery to be asap are higher
            order.now = np.random.choice([True,False], p=[0.7,0.3])
        else:
            order.now = np.random.choice([True,False])
        if not order.now:
            # Determine the delivery date
            order.delivery_date = generateDate(order.date, range(1,8),
                delivery_params['dist'], delivery_params['prob'], range(0,60,5))

        order.sharing = np.random.choice([True,False])
        # Determine the flexibility span the user agrees to
        order.flexibility = np.random.choice(range(0,31,5),p=[0.05,0.1,0.2,0.3,0.2,0.1,0.05])

        # Determine the number of Items
        nb_items = np.random.choice(range(1, order_params['max_items']+1))
        items_list = []
        for i in range(nb_items):
            element = np.random.choice(order_params['list'])
            if not updateDictInList(items_list, element['name']):
                element['amount'] = 1
                items_list.append(element)
        order.items = items_list
        order.compute_order_full_cost(delivery_params['charge'], 2)
        orders.append(order)
    return orders, generatedPositions
