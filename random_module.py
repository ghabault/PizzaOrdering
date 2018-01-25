import numpy as np
from datetime import datetime, timedelta
from order import *

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

def generateOrderList(date_start, date_end, names, order_params, delivery_params,
    position_limits):
    start_dt = datetime.strptime(date_start, "%Y-%m-%dT%H:%M")
    end_dt = datetime.strptime(date_start, "%Y-%m-%dT%H:%M")

    orders = []
    for i in range(order_params['num']):
        order = Order()
        # Choose a customer Name and phone number
        order.name = np.random.choice(names)
        order.phone = generatePhoneNumber()
        # Determine the delivery shop_address
        #order.delivery_address = generateDeliveryAddress(position_limits)
        # Determine the order date
        order.date = generateDate(start_dt, range(0,(end_dt-start_dt).days+1), order_params['dist'], order_params['prob'], range(0,60))

        # Determine if the delivery is asap or planned
        if compareTimes(order.date, "08:00", "22:00"):
            # Between 22:00 and 08:00 the chance for the delivery to be asap are higher
            order.now = np.random.choice([True,False], p=[0.7,0.3])
        else:
            order.now = np.random.choice([True,False])
        if not order.now:
            # Determine the delivery date
            order.delivery_date = generateDate(order.date, range(1,8), delivery_params['dist'], delivery_params['prob'], range(0,60,5))

        # Determine the sharing span the user agrees to
        order.sharing_span = np.random.choice(range(0,31,5),p=[0.05,0.1,0.2,0.3,0.2,0.1,0.05])

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
    return orders