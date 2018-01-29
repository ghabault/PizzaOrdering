from datetime import datetime, timedelta
import re, ast
import requests
import json
####
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
####
from random_module import *
from order import *
from flask import Flask, render_template, request, redirect, url_for, abort, session, Markup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D';

hour_dist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
    19, 20, 21, 22, 23]
order_prob = [0.0405, 0.027, 0.0135, 0.0135, 0.0005, 0.0005, 0.0135, 0.0135,
    0.027, 0.027, 0.0405, 0.054, 0.0675, 0.054, 0.054, 0.0405, 0.0405, 0.054,
    0.0675, 0.0675, 0.081, 0.081, 0.0675, 0.054]

# CONFIG
DMS_URL = "https://automatic-vehicle.herokuapp.com/"
ORDER_KEY = "order_management.php"
TS_FORMAT = "%Y-%m-%dT%H:%M"

# Shop information
SHOP_NAME = "Pizza'Bunga"
SHOP_ADDRESS = "4-31-8 Kizuki, Nakahara-ku, Kawazaki-shi, Kanagawa-ken 211-0025"
SHOP_PHONE = "080-4627-6196"

# cooking delay
COOKING_DELAY = 5

# maximum number of pizzas to order
MAX_PIZZAS = 5

# delivery charge in $
DELIVERY_CHARGE = 3.00
# Maximum time that pizzas can wait after being prepared before delivered in minutes
MAX_KEEP_PIZZAS = 10

PIZZAS_AVAILABLE = (
    {"name": "Hawaiian",             "price": 8.5,  "time": 2},
    {"name": "Meat Lovers",          "price": 8.5,  "time": 2},
    {"name": "Pepperoni",            "price": 8.5,  "time": 2},
    {"name": "Ham & Cheese",         "price": 9.5,  "time": 3},
    {"name": "Classic Cheese",       "price": 9.5,  "time": 2},
    {"name": "Veg Hot 'n' Spicy",    "price": 9.5,  "time": 3},
    {"name": "Beef & Onion",         "price": 9.5,  "time": 3},
    {"name": "Seafood Deluxe",       "price": 13.5, "time": 4},
    {"name": "Summer Shrimp",        "price": 13.5, "time": 4},
    {"name": "BBQ Bacon & Mushroom", "price": 13.5, "time": 4},
    {"name": "BBQ Hawaiian",         "price": 13.5, "time": 4},
    {"name": "Italiano",             "price": 13.5, "time": 4},
)


def get_delay(delivery_addr):
    """Send the customer information to the Delivery Management System, and receive delay"""
    delivery_delay = 0
    order_id = 0
    webpath = DMS_URL + ORDER_KEY

    payload = make_getcmd_json(SHOP_ADDRESS, delivery_addr)
    #print payload
    websource = requests.get(webpath, json=payload, auth=('yamanaka', 'yamanaka'))
    try:
        response = json.loads(websource.text)
        #print json.dumps(response, sort_keys=True, indent=4, separators=(',', ': '))
        delay = response['duration']
        oid = response['order_id']
        if delay is None:
            #print "Not receiving delay information"
            #print "Request = " + str(payload)
            #print "Response = " + str(websource.text)
            #print delay, oid
            return 0, oid
        else:
            delivery_delay = re.findall('\d+', str(delay))
            #print delay, oid
            return int(delivery_delay[0]), oid
    except(ValueError, KeyError, TypeError):
        #print "JSON format error"
        #print str(websource.text)
        return 0, 0

def send_order(order, generation_type):
    webpath = DMS_URL + ORDER_KEY
    payload = get_json_payload(order, generation_type)

    #print str(json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': ')))
    websource = requests.post(webpath, json=payload, auth=('yamanaka', 'yamanaka'))
    return websource.status_code

def make_getcmd_json(origin_address, destination_address):
    data = {"information":{"origin":origin_address, "destination":destination_address}}
    return data

def make_dinfo_json(customer_name, customer_phone, customer_address, customer_message, delivery_date, sharing_span):
    data = {"name":customer_name,"phone":customer_phone,
        "address":customer_address, "message":customer_message,
        "date":delivery_date, "dFormat":TS_FORMAT, "sharing":sharing_span}
    return data

def make_sinfo_json(shop_name, shop_phone, shop_address):
    data = {"name":shop_name,"phone":shop_phone,"address":shop_address}
    return data

def make_order_json(order_id, generation_type, order_date, order_preparation, order_max_keep, order_list):
    data = {"id":order_id, "generatedBy":generation_type, "date":order_date,
        "dFormat":TS_FORMAT, "preparation":order_preparation, "pUnit":"min",
        "keeptime": order_max_keep, "kUnit":"min", "list":order_list, "lType":"pizza"}
    return data

def get_json_payload(order, generation_type):
    sinfo = make_sinfo_json(SHOP_NAME, SHOP_PHONE, SHOP_ADDRESS)
    if order.now:
        date = ""
    else:
        date = order.delivery_date.strftime(TS_FORMAT)
    dinfo = make_dinfo_json(order.name, order.phone, order.delivery_address,
        order.message, date, order.sharing_span)
    oinfo = make_order_json(order.ID, generation_type, order.date.strftime(TS_FORMAT), order.preparation_time, order.max_keep_time, order.items)
    data = {"information":{"shop":sinfo, "delivery":dinfo, "order":oinfo}}
    return data

def format_table_row(l_num, l_sym, l_text, c_num, c_sym, c_text, r_num, r_sym, r_text):
    row = """
        <tr>
            <td> {}{}{} </td>
            <td> {}{}{} </td>
            <td> {}{}{} </td>
        </tr>
    """.format(l_num, l_sym, l_text, c_num, c_sym, c_text, r_num, r_sym, r_text)

    return row



@app.route('/')
def home():
    return render_template('index.html', now=str(datetime.now().strftime(TS_FORMAT)))

@app.route('/script')
def script():
    return render_template('script.html')

@app.route('/random', methods=['POST'])
def random():
    #### Variables for generation
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

    def getAxisPoints(source_list):
        xs = []
        ys = []

        for element in source_list:
            xs.append(element[0])
            ys.append(element[1])

        return xs, ys

    #### Input from user
    session['start_date'] = request.form['start_date']
    session['end_date'] = request.form['end_date']
    session['nb_orders'] = request.form['nb_orders']
    session['delivery_charge'] = request.form['delivery_charge']
    session['max_items'] = request.form['max_items']
    session['area_limits'] = ast.literal_eval(request.form['area_limits'])
    session['seed'] = int(request.form['seed'])

    # inputs = session['area_limits'].split(",")
    orders = []
    positions = []

    np.random.seed(session['seed'])

    order_params = {'dist':hour_dist, 'prob':order_prob, 'num':int(session['nb_orders']),
        'max_items':int(session['max_items']), 'list':PIZZAS_AVAILABLE}
    delivery_params = {'dist':hour_dist, 'prob':delivery_prob, 'charge':int(session['delivery_charge'])}

    orders, positions = generateOrderList(session['start_date'], session['end_date'],
        customer_names, order_params, delivery_params, session['area_limits'])

    for order in orders:
        order.compute_order_full_delay(COOKING_DELAY)

    generated_distribution = generatedDists(orders)
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
    xs, ys = getAxisPoints(session['area_limits'])
    plt.plot(xs, ys, '--')
    xs, ys = getAxisPoints(positions)
    plt.plot(xs, ys, 'bo')

    plt.suptitle("Generated distributions", y=1)
    plt.tight_layout()

    #strio = StringIO.StringIO()
    strio = io.StringIO()
    fig.savefig(strio, format="svg")
    plt.close(fig)

    strio.seek(0)
    #svgstr = strio.buf[strio.buf.find("<svg"):]
    svgstr = '<svg' + strio.getvalue().split('<svg')[1]
    return render_template('analysis.html', start_dt=session['start_date'],
        end_dt=session['end_date'], nb_orders=session['nb_orders'],
        seed=session['seed'], num_generation=len(orders),
        img_analysis=Markup(svgstr.decode("utf-8")))
        #img_analysis=Markup(unicode(svgstr, "utf-8")))

@app.route('/signup', methods=['POST'])
def signup():
    session['customer_name'] = request.form['customer_name']
    session['customer_phone'] = request.form['customer_phone']
    session['delivery_addr'] = request.form['delivery_addr']
    session['delivery_date'] = request.form['delivery_date']
    session['sharing_span'] = request.form.get("sharing_span")
    session['nb_pizza'] = request.form['nb_pizza']
    session['message'] = request.form['message']
    if session['delivery_addr']:
        session['delivery_delay'], session['order_id'] = get_delay(session['delivery_addr'])
        #print session['delivery_delay']
    return redirect(url_for('order_page'))

@app.route('/order')
def order_page():
    menu = """
    """
    menu += format_table_row("", "", "<strong>Number</strong>", "", "", "<strong>Name</strong>", "", "", "<strong>Price</strong>")
    for i, pizza in enumerate(PIZZAS_AVAILABLE):
        # each pizza's number is its index (i) + 1,
        # so the first pizza is 1
        menu += format_table_row("", "#", str(i+1).zfill(2), "", "", pizza["name"], "", "$ ", str(pizza["price"]))
    menu = Markup(menu)
    return render_template('order.html', menu=menu, nb_items=session['nb_pizza'])


@app.route('/message', methods=['POST'])
def message():
    session['customer_selection'] = request.form['customer_selection']
    if not 'customer_name' in session:
        return abort(403)
    order = Order()
    order.name = session['customer_name']
    order.phone = session['customer_phone']
    order.message = session['message']
    if session['delivery_addr']:
        order.ID = session['order_id']
        order.pickup = False
        order.delivery_address = session['delivery_addr']
        order.delay = session['delivery_delay']
        order.sharing_span = int(session['sharing_span'])
    else:
        order.pickup = True
    if session['delivery_date']:
        order.delivery_date = datetime.strptime(session['delivery_date'], TS_FORMAT)
        order.now = False

    pizza_list = session['customer_selection'].strip().split(",")
    # print pizza_list
    order.set_items(int(session['nb_pizza']), pizza_list, PIZZAS_AVAILABLE)
    order.compute_order_full_cost(DELIVERY_CHARGE, 2)
    order.max_keep_time = MAX_KEEP_PIZZAS
    order.compute_order_full_delay(COOKING_DELAY)
    order.date = datetime.now()

    bill = """
    """
    bill += format_table_row("", "", "<strong>Order summary:</strong>", "", "", "<strong>Price each:</strong>", "", "", "<strong>Subtotal:</strong>")
    for item in order.items:
        bill += format_table_row(item["amount"], "x", item["name"], "", "$ ", item["price"], "", "$ ", item["price"]*item["amount"])

    sharing_txt = "approx."
    if not order.pickup:
        bill += format_table_row("", "", "Delivery charge", "", "", "", "", "$ ", DELIVERY_CHARGE)
        if order.sharing_span is not 0:
            bill += format_table_row("", "", "Sharing option discount", "", "", "", "-", "$ ", order.delivery_discount)
            sharing_txt = "+/- {} mins".format(order.sharing_span)

    # print the line before total
    bill += format_table_row("", "", "", "", "", "", "", "", "----------")

    # print the total of the order
    bill += format_table_row("", "", "", "", "", "<strong>Total:</strong>", "", "<strong>$ </strong>", order.total_cost)

    bill = Markup(bill)

    if order.delivery_date is not None:
        #final_date = order.delivery_date + timedelta(minutes = int(order.total_delay))
        final_date = order.delivery_date
        if order.pickup:
            delay_msg = "Will be ready on: {:3} min ({})".format(final_date.strftime(TS_FORMAT), sharing_txt)
            return render_template('message.html', name=order.name,
                                                   date=order.date.strftime(TS_FORMAT),
                                                   type="Pickup",
                                                   delay_msg=delay_msg,
                                                   bill=bill,
                                                   phone=session['customer_phone'],
                                                   message=session['message'])
        else:
            response_code = send_order(order, "website")
            if(response_code == 200):

                if order.delay == 0:
                    delay_msg = "Delivered on: Unknown"
                else:
                    delay_msg = "Delivered on: {:3} min ({})".format(final_date.strftime(TS_FORMAT), sharing_txt)
                addr_msg = Markup("<strong>Delivery address:</strong> " + session['delivery_addr'])
                return render_template('message.html', name=order.name,
                                                      date=order.date.strftime(TS_FORMAT),
                                                      type="Delivery",
                                                      delay_msg=delay_msg,
                                                      addr=addr_msg,
                                                      bill=bill,
                                                      phone=session['customer_phone'],
                                                      message=session['message'])
            else:
                pass
               #print "We have not been able to contact the delivery system."
    else:
        if order.pickup:
            delay_msg = "Ready in: {:3} minutes ({})".format(order.total_delay, sharing_txt)
            return render_template('message.html', name=order.name,
                                                   date=order.date.strftime(TS_FORMAT),
                                                   type="Pickup",
                                                   delay_msg=delay_msg,
                                                   bill=bill,
                                                   phone=session['customer_phone'],
                                                   message=session['message'])
        else:
            response_code = send_order(order, "website")
            #print response_code
            if(response_code == 200):
                if order.delay == 0:
                    delay_msg = "Delivered in: Unknown"
                else:
                    delay_msg = "Delivered in: {:3} minutes ({})".format(order.total_delay, sharing_txt)
                addr_msg = Markup("<strong>Delivery address:</strong> " + session['delivery_addr'])
                return render_template('message.html', name=order.name,
                                                      date=order.date,
                                                      type="Delivery",
                                                      delay_msg=delay_msg,
                                                      addr=addr_msg,
                                                      bill=bill,
                                                      phone=session['customer_phone'],
                                                      message=session['message'])
            else:
                pass
                #print "We have not been able to contact the delivery system."





if __name__ == '__main__':
    PIZZAS_AVAILABLE = sorted(
        PIZZAS_AVAILABLE,
        key=lambda k: (k["price"], k["name"]))

    app.run()
