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

nb_orders = 100
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

inp_bounds = [{'lat': 35.55852843647213, 'long': 139.64362022274145},
        {'lat': 35.55876409598856, 'long': 139.64411911361822},
        {'lat': 35.55916558838372, 'long': 139.6447843014539},
        {'lat': 35.559252869073056, 'long': 139.64547094696172},
        {'lat': 35.559252869073056, 'long': 139.64598593109258},
        {'lat': 35.559252869073056, 'long': 139.64652237289556},
        {'lat': 35.559444886255065, 'long': 139.6468013226331},
        {'lat': 35.55953216664026, 'long': 139.64720901840337},
        {'lat': 35.5598114632342, 'long': 139.6474665104688},
        {'lat': 35.559933655188, 'long': 139.64796003692754},
        {'lat': 35.557961105164765, 'long': 139.65107139938482},
        {'lat': 35.55722793260436, 'long': 139.65229448702303},
        {'lat': 35.556808973844596, 'long': 139.65298113253084},
        {'lat': 35.55618053159912, 'long': 139.65469774630037},
        {'lat': 35.55586630862876, 'long': 139.65566334154573},
        {'lat': 35.555482256658905, 'long': 139.65658602144686},
        {'lat': 35.555202944979676, 'long': 139.6571868362662},
        {'lat': 35.55460940442998, 'long': 139.65806660082308},
        {'lat': 35.554120603030405, 'long': 139.65815243151155},
        {'lat': 35.55371908536543, 'long': 139.65795931246248},
        {'lat': 35.55263672338184, 'long': 139.6575301590201},
        {'lat': 35.55190350212271, 'long': 139.6574228706595},
        {'lat': 35.55085603154859, 'long': 139.6572941246268},
        {'lat': 35.549808547289295, 'long': 139.65699371721712},
        {'lat': 35.54879596616366, 'long': 139.65682205584017},
        {'lat': 35.54589781847485, 'long': 139.6556204262015},
        {'lat': 35.5447105952031, 'long': 139.65510544207064},
        {'lat': 35.54352335435482, 'long': 139.65459045793978},
        {'lat': 35.542790049756206, 'long': 139.65424713518587},
        {'lat': 35.541358340501006, 'long': 139.65398964312044},
        {'lat': 35.54083453804631, 'long': 139.65390381243196},
        {'lat': 35.539088505157814, 'long': 139.654268592858},
        {'lat': 35.53842500269417, 'long': 139.65199407961336},
        {'lat': 35.53762180815809, 'long': 139.65049204256502},
        {'lat': 35.536434462372725, 'long': 139.64907583620516},
        {'lat': 35.537028137462286, 'long': 139.64806732561556},
        {'lat': 35.53805832792545, 'long': 139.6464365425345},
        {'lat': 35.54038930327015, 'long': 139.64224545658453},
        {'lat': 35.54154603554805, 'long': 139.63899656385593},
        {'lat': 35.542894807966505, 'long': 139.6342485844434},
        {'lat': 35.54519945397306, 'long': 139.63517126434454},
        {'lat': 35.54593273654031, 'long': 139.63216719024786},
        {'lat': 35.54986092182727, 'long': 139.63388380409924},
        {'lat': 35.55000058709465, 'long': 139.63480648400036},
        {'lat': 35.550210084539515, 'long': 139.63512834908215},
        {'lat': 35.550419581437005, 'long': 139.63684496285168},
        {'lat': 35.55261926581076, 'long': 139.63570770622937},
        {'lat': 35.55335248052367, 'long': 139.63637289406506},
        {'lat': 35.55476651853257, 'long': 139.63585790991374},
        {'lat': 35.55469669008054, 'long': 139.63697370886393},
        {'lat': 35.555115659880336, 'long': 139.63740286230632},
        {'lat': 35.55588376549275, 'long': 139.63796076178141},
        {'lat': 35.55560445521253, 'long': 139.63886198401042},
        {'lat': 35.555394971863706, 'long': 139.63941988348552},
        {'lat': 35.55556954135907, 'long': 139.64057859777995},
        {'lat': 35.55588376549275, 'long': 139.64137253164836},
        {'lat': 35.55619798839467, 'long': 139.6423166692216},
        {'lat': 35.55665186374513, 'long': 139.64306768774577},
        {'lat': 35.55689625710013, 'long': 139.64386162161418},
        {'lat': 35.5575246937343, 'long': 139.6436685025651},
        {'lat': 35.55795892236515, 'long': 139.64386698531644},
        {'lat': 35.5582622276664, 'long': 139.64397963881083},
        {'lat': 35.558408424437864, 'long': 139.643837482}]

area_bounds = [[d['lat'],d['long']] for d in inp_bounds]
print area_bounds


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
    oinfo = make_order_json(order.ID, "script", order.date.strftime("%Y-%m-%dT%H:%M"),
        order.preparation_time, order.max_keep_time, order.items)
    data = {"information":{"shop":shop_json, "delivery":dinfo, "order":oinfo}}
    return data

generated_orders, generated_positions = generateOrderList(start_date, end_date, customer_names,
    order_params, delivery_params, area_bounds)

for order in generated_orders:
    #order.compute_order_full_delay()
    json_data = get_json_payload(order)
    pprint.pprint(json_data)
    print "----------------------------------------------------------------"

generated_distribution = generatedDists(generated_orders)

def getAxisPoints(source_list):
    xs = []
    ys = []

    for element in source_list:
        xs.append(element[0])
        ys.append(element[1])

    return xs, ys

fig = plt.figure()
ax1 = plt.subplot2grid((4,5), (0,0), rowspan=2, colspan=2)
ax1.set_title("Orders hour")
ax1.set_xlim(0,24)
sns.distplot(generated_distribution['order'])
ax2 = plt.subplot2grid((4,5), (2,0), rowspan=2, colspan=2)
ax2.set_title("Deliveries hour")
ax2.set_xlim(0,24)
sns.distplot(generated_distribution['delivery'])
ax3 = plt.subplot2grid((4,5), (0,2), colspan=3, rowspan=4)
ax3.set_title("Orders position")
xs, ys = getAxisPoints(area_bounds)
plt.plot(xs, ys, '--')
xs, ys = getAxisPoints(generated_positions)
plt.plot(xs, ys, 'bo')
# ax4 = plt.subplot2grid((4,4), (2,2), colspan=2, rowspan=2)
# ax4.set_title("Orders position")
# sns.jointplot(x=np.array(xs), y=np.array(ys), kind="hex", color="k")

plt.suptitle("Generated distributions")
plt.tight_layout()

plt.show()
