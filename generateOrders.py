from datetime import datetime, timedelta
import numpy as np
import pprint
from app import DELIVERY_CHARGE, PIZZAS_AVAILABLE, make_dinfo_json, make_order_json
from random_module import *

import seaborn as sns
import matplotlib.pyplot as plt

print np.version.version

start_date = "2018-01-24T00:00"
end_date = "2018-01-31T23:00"

nb_orders = 1000
seed = 150

customer_names = ["Iwasaki","Nakajima","Imakiire","Kamio","Takemura","Hirono",
    "Yamashita","Aoki","Sekigawa","Mikuni","Yarita","Kubokawa","Hara","Fukumoto",
    "Murakami","Yamada","Osuna","Yamamoto","Miyazaki","Aoi"]

hour_dist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
    19, 20, 21, 22, 23]
order_prob = [0.0405, 0.027, 0.0135, 0.0135, 0.0005, 0.0005, 0.0135, 0.0135,
    0.027, 0.027, 0.0405, 0.054, 0.0675, 0.054, 0.054, 0.0405, 0.0405, 0.054,
    0.0675, 0.0675, 0.081, 0.081, 0.0675, 0.054]
delivery_prob = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0481,
    0.12025, 0.12025, 0.0481, 0.0034875, 0.0034875, 0.0034875, 0.0034875, 0.0481,
    0.21645, 0.21645, 0.12025, 0.0481, 0.0]

order_params = {'dist':hour_dist, 'prob':order_prob, 'num':nb_orders,
    'max_items':5, 'list':PIZZAS_AVAILABLE}
delivery_params = {'dist':hour_dist, 'prob':delivery_prob, 'charge':DELIVERY_CHARGE}

shop_json = {"name":"Pizza'Bunga","phone":"080-4627-6196","address":"4-31-8 Kizuki, Nakahara-ku, Kawazaki-shi, Kanagawa-ken 211-0025"}


np.random.seed(seed)

def get_json_payload(order):
    if order.now:
        date = ""
    else:
        date = order.delivery_date.strftime("%Y-%m-%dT%H:%M")
    dinfo = make_dinfo_json(order.name, order.phone, order.delivery_address,
        order.message, date, order.sharing_span)
    oinfo = make_order_json(order.ID, order.date.strftime("%Y-%m-%dT%H:%M"), order.preparation_time, order.max_keep_time, order.items)
    data = {"information":{"shop":shop_json, "delivery":dinfo, "order":oinfo}}
    return data

generated_orders = generateOrderList(start_date, end_date, customer_names, order_params, delivery_params, [0,0,0,0])

for order in generated_orders:
    #order.compute_order_full_delay()
    json_data = get_json_payload(order)
    pprint.pprint(json_data)
    print "----------------------------------------------------------------"

generated_distribution = generatedDists(generated_orders)

fig = plt.figure()
ax1 = plt.subplot2grid((4,4), (0,0), rowspan=2)
ax1.set_title("Orders hour")
ax1.set_xlim(0,24)
sns.distplot(generated_distribution['order'])
ax2 = plt.subplot2grid((4,4), (2,0), rowspan=2)
ax2.set_title("Deliveries hour")
ax2.set_xlim(0,24)
sns.distplot(generated_distribution['delivery'])
ax3 = plt.subplot2grid((4,4), (0,1), colspan=3, rowspan=4)
ax3.set_title("Orders position")

plt.tight_layout()
plt.suptitle("Generated distributions")
plt.show()
